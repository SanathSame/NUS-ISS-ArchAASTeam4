"""Nodes for the Assignment 4 (JobConnect) workflow.

This mirrors the `3-workshop/nodes.py` structure but adapted for the job search
multi-agent flow. The nodes are intentionally defensive: they import agent
constructors lazily, create LLMs using an optional compatibility helper if present,
and run agent `process(...)` methods using asyncio when the agent is async.

Nodes provided:
- human_node: collects user input (upload resume / set preferences / search / exit)
- check_exit_condition: checks if user asked to end
- coordinator_routing: asks the router which agent should run next
- participant_node: runs the selected agent and updates state
- summarizer_node: prints a final summary

This file should be executed from the `Assignment 4/` folder so relative imports
resolve and `Assignment 4/.env` can be found by dotenv helpers.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, Optional

# State type is defined in state.py at package root
from state import JobSearchState, JobSearchStage

# Router and agents are imported lazily to avoid import-time LLM construction


def human_node(state: JobSearchState) -> Dict:
    """Collect user input and update state.

    Supported quick commands:
    - upload: prompt for resume file path (text or pdf). The file contents are
      read into state["resume_text"] so the Resume Parser agent can consume it.
    - prefs: prompt for job preferences (location, job type, keywords)
    - search: mark the search_query from previously-set preferences and continue
    - show: display current state summary
    - exit: will trigger the summarizer via check_exit_condition

    Returns a partial state dict to merge into the global state.
    """
    print("\nJobConnect — enter a command (upload / prefs / search / show / exit):")
    cmd = input("> ").strip().lower()

    messages = state.get("messages", []).copy()
    messages.append({"role": "user", "content": f"command: {cmd}"})

    updates: Dict = {"messages": messages}

    if cmd in ("upload", "u"):
        path = input("Enter path to resume (txt or pdf): ").strip()
        file = Path(path)
        if file.exists():
            try:
                # read as text when possible; for pdf we keep path for a parser
                if file.suffix.lower() == ".pdf":
                    # store path and let a parser tool handle PDF extraction
                    updates["resume_path"] = str(file.absolute())
                    updates["messages"] = messages + [{"role": "system", "content": f"Received resume file: {file.name}"}]
                else:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                    updates["resume_text"] = text
                    updates["messages"] = messages + [{"role": "system", "content": f"Loaded resume text ({len(text)} chars)"}]
            except Exception as e:
                updates["messages"] = messages + [{"role": "system", "content": f"Error reading file: {e}"}]
        else:
            updates["messages"] = messages + [{"role": "system", "content": "File not found."}]

    elif cmd in ("prefs", "preferences"):
        loc = input("Preferred location (press Enter to skip): ").strip()
        job_type = input("Job type (Full-time / Part-time / Remote / Any): ").strip() or "Any"
        keywords = input("Keywords (comma-separated, press Enter to skip): ").strip()
        prefs = {"location": loc or None, "job_type": job_type, "keywords": [k.strip() for k in keywords.split(",") if k.strip()]} if (loc or keywords) else {"job_type": job_type}
        updates["search_query"] = prefs
        updates["messages"] = messages + [{"role": "system", "content": f"Search preferences saved: {prefs}"}]

    elif cmd in ("search", "s"):
        # If user typed search, ensure we have a query; if not use defaults
        if not state.get("search_query"):
            print("No preferences set — using default search (keywords from resume if available)")
            updates["search_query"] = {"keywords": state.get("resume_data", {}).get("skills", [])} if state.get("resume_data") else {"keywords": []}
        # advance stage if appropriate
        updates["messages"] = messages + [{"role": "system", "content": "Search requested"}]

    elif cmd in ("show", "status"):
        # Print a tiny summary to the console and don't change workflow stage
        print("\n--- Current State Summary ---")
        print(f"Stage: {state.get('stage')}")
        if state.get("resume_data"):
            print(f"Resume parsed: skills={len(state['resume_data'].get('skills', []))} experiences={len(state['resume_data'].get('experience', []))}")
        else:
            print("Resume: none")
        if state.get("job_listings"):
            print(f"Found jobs: {len(state['job_listings'])}")
        else:
            print("Found jobs: 0")
        print("--- end summary ---\n")

    elif cmd in ("exit", "quit"):
        updates["messages"] = messages + [{"role": "system", "content": "User requested exit"}]

    else:
        updates["messages"] = messages + [{"role": "system", "content": "Unknown command"}]

    # By default keep stage unchanged; agents/nodes will update it when they run
    return updates


def check_exit_condition(state: JobSearchState) -> str:
    """Return the next node name based on whether user typed exit.

    Mirrors the boolean check in the workshop version: if last message contains
    'exit' we move to the summarizer, otherwise continue to the coordinator.
    """
    messages = state.get("messages", [])
    if messages:
        last = messages[-1]
        if "exit" in last.get("content", "").lower():
            return "summarizer"
    return "coordinator"


def coordinator_routing(state: JobSearchState) -> str:
    """Ask the JobSearchRouter which agent should run next.

    Returns node name strings that map to the participant node, human node or end.
    """
    try:
        from agents.router import JobSearchRouter
        router = JobSearchRouter()
        next_agent, config = router.route(state)
        # normalize returned names to node targets
        if next_agent == "resume_parser":
            return "participant"
        if next_agent == "job_searcher":
            return "participant"
        if next_agent == "relevance_scorer":
            return "participant"
        if next_agent == "content_generator":
            return "participant"
        if next_agent == "end":
            return "summarizer"
        # default to human so user can direct next action
        return "human"
    except Exception as e:
        # If router fails, fall back to human input
        print(f"Router error: {e}")
        return "human"


def _create_agent_instance(name: str):
    """Factory: create an agent instance by name with safe LLM construction.

    The function tries common patterns:
    - import an agent class from `agents.<name>`
    - if the class requires an LLM it will attempt to construct one via
      `utils.llm_compat.get_chat_llm()` if available.

    Returns the agent instance or raises ImportError.
    """
    # mapping from logical name to module/class names
    mapping = {
        "resume_parser": ("agents.resume_parser", "ResumeParserAgent"),
        "job_searcher": ("agents.job_searcher", "JobSearchAgent"),
        "relevance_scorer": ("agents.relevance_scorer", "RelevanceScorerAgent"),
        "content_generator": ("agents.content_generator", "ContentGeneratorAgent"),
    }
    if name not in mapping:
        raise ImportError(f"Unknown agent: {name}")

    module_name, class_name = mapping[name]
    module = __import__(module_name, fromlist=[class_name])
    AgentClass = getattr(module, class_name)

    # Try to construct an LLM if the agent appears to need one
    try:
        # look for a helper that centralizes LLM creation
        llm = None
        try:
            from utils.llm_compat import get_chat_llm
            llm = get_chat_llm()
        except Exception:
            llm = None

        # instantiate depending on constructor signature
        if llm is not None:
            try:
                return AgentClass(llm)
            except TypeError:
                # Agent doesn't accept llm in constructor
                return AgentClass()
        else:
            return AgentClass()
    except Exception as e:
        # re-raise with context
        raise ImportError(f"Failed to create agent {name}: {e}")


def participant_node(state: JobSearchState) -> Dict:
    """Run the agent indicated by the router and merge its state updates.

    The router stores the logical next agent name in the state under
    `next_agent` (e.g. "resume_parser"). This node will instantiate the
    appropriate agent and call its `process(state)` method. The agent may be
    synchronous or asynchronous; we handle both.

    Returns a partial state dict of updates to merge.
    """
    next_agent = state.get("next_agent")
    if not next_agent:
        # nothing to do
        return {}

    try:
        agent = _create_agent_instance(next_agent)
    except ImportError as e:
        return {"messages": state.get("messages", []) + [{"role": "system", "content": f"Agent load error: {e}"}], "error": str(e)}

    # Call process(...) on the agent; adapt to return types we saw earlier
    try:
        # Many agents implement async process(state)
        if asyncio.iscoroutinefunction(getattr(agent, "process", None)):
            updated = asyncio.run(agent.process(state))
        else:
            # sync process may return new state or a tuple
            updated = agent.process(state)

        # Agents in some implementations return the whole updated state; others
        # return tuples (messages, state) — handle both patterns.
        if isinstance(updated, tuple) and len(updated) == 2:
            # (messages_or_list, new_state)
            _, new_state = updated
            return new_state
        elif isinstance(updated, dict):
            return updated
        else:
            # If agent returned None or unexpected we assume it mutated `state`.
            return {k: v for k, v in state.items()}

    except Exception as e:
        return {"messages": state.get("messages", []) + [{"role": "system", "content": f"Agent runtime error: {e}"}], "error": str(e)}


def summarizer_node(state: JobSearchState) -> Dict:
    """Create a short end-of-workflow summary and print results.

    If job matches have been generated, show top 5 matches and their scores.
    """
    print("\n=== JOBCONNECT SUMMARY ===\n")

    if state.get("relevance_scores") and state.get("job_listings"):
        scores = state["relevance_scores"]
        jobs = {job["id"]: job for job in state["job_listings"]}
        # sort by total_score if present
        sorted_items = sorted(scores.items(), key=lambda kv: kv[1].get("total_score", 0), reverse=True)
        print("Top matches:")
        for rank, (job_id, score_obj) in enumerate(sorted_items[:5], start=1):
            job = jobs.get(job_id)
            if not job:
                continue
            print(f"{rank}. {job['title']} @ {job['company']} ({job['location']}) — score: {score_obj.get('total_score', 0):.2f}")
            print(f"   Skills: {score_obj.get('skill_score'):.2f}, Exp: {score_obj.get('experience_score'):.2f}")
    else:
        print("No scored job matches to show.")

    print("\nThank you for using JobConnect — good luck with your applications!")

    return {}
