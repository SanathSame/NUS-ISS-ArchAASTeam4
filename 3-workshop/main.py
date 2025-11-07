# main.py
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import random

from state import State
from nodes import (
    human_node,
    check_exit_condition,
    coordinator_routing,
    participant_node,
    summarizer_node,
)
from agents.coordinator import coordinator
from agents.resume_parser import load_resume_from_file

def get_user_input() -> tuple[str, str] | None:
    """
    Ask the user for a resume file path and job query.
    Returns (resume_text, job_query), or None if user typed exit.
    """
    print("\n=== JOB CONNECT DEMO ===")
    resume_path = input("Enter path to your resume file (or type 'exit' to quit): ").strip()
    if resume_path.lower() == "exit":
        return None

    try:
        resume_text = load_resume_from_file(resume_path)
    except FileNotFoundError:
        print(f"[Error] File '{resume_path}' not found. Try again.\n")
        return get_user_input()  # retry

    job_query = input("Enter job search keywords (or type 'exit' to quit): ").strip()
    if job_query.lower() == "exit":
        return None

    return resume_text, job_query

def build_graph():
    builder = StateGraph(State)
    builder.add_node("human", human_node)
    builder.add_node("coordinator", coordinator)
    builder.add_node("participant", participant_node)
    builder.add_node("summarizer", summarizer_node)

    builder.add_edge(START, "coordinator")
    builder.add_conditional_edges(
        "human", 
        check_exit_condition, 
        {
            "summarizer": "summarizer",     # exit flow
            "coordinator": "coordinator"    # normal flow
        }
    )
    # Coordinator decides whether to go to participant or human
    builder.add_conditional_edges(
        "coordinator", 
        coordinator_routing, 
        {
            "participant": "participant",   # next pipeline step
            "human": END,                # pipeline completed, prompt user again
            "summarizer": "summarizer",     # exit
        }
    )
    # After participant finishes one step, go back to coordinator
    builder.add_edge("participant", "coordinator")
    # Summarizer ends the flow
    builder.add_edge("summarizer", END)
    return builder.compile()


def main():
    load_dotenv(override=True)

    graph = build_graph()
    print(graph.get_graph().draw_ascii())

    while True:
        user_input = get_user_input()
        if not user_input:
            # User typed exit at resume/job input → run summarizer
            summarizer_node(initial_state)
            break

        resume_text, job_query = user_input
        print(f"\n[INPUT] Resume and job query ready.")
        print(f"       Resume: \n{resume_text}")
        print(f"       Query : \n{job_query}\n")
        print("\n[INFO] Running full job connect pipeline...\n")

        # If initial_state exists from previous runs, preserve messages
        prev_messages = []
        if 'initial_state' in locals() and 'messages' in initial_state:
            prev_messages = initial_state['messages']

        # create new state for this resume
        initial_state = State(
            messages=prev_messages,   # preserve messages
            volley_msg_left=1,        # one run per resume
            next_agent=None,
            stage_idx=0,
            resume_text=resume_text,
            job_query=job_query
        )

        # initial_state = State(
        #     messages=[],
        #     volley_msg_left=1, # one run per resume
        #     next_agent=None,
        #     resume_text=resume_text,
        #     job_query=job_query,
        #     stage_idx=0,  # start at the first agent
        # )

    # # Get resume from file
    # resume_text = load_resume_from_file()
    # print("\n✅ Resume file loaded successfully.\n")
    # Ask user for job query keywords
    # job_query = input("Enter job search keywords separated by space (e.g. 'python angular singapore'): ").strip()
    # if not job_query:
    #     job_query = "software engineer singapore"
    #     print(f"(Using default query: {job_query})")

        try:
            graph.invoke(initial_state, config={"recursion_limit": 100})
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Ending conversation...")

        again = input("\nWould you like to process another resume? (y/n): ").strip().lower()
        if again != "y":
            final_state = graph.invoke(initial_state, config={"recursion_limit": 100})
            summarizer_node(final_state)    
            break

if __name__ == "__main__":
    main()
