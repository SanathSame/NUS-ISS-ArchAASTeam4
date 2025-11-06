from typing import Any, Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from state import State

class RelevanceScorerAgent:
    """Agent responsible for scoring job matches against resume."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at matching job requirements with candidate qualifications.
            Analyze the job description and resume to:
            1. Compare required skills vs candidate skills
            2. Evaluate experience level match
            3. Assess cultural fit indicators
            4. Consider location and other preferences
            Score each aspect and provide an overall match percentage and detailed explanation."""),
            ("user", "Job Description: {job_description}\nResume Data: {resume_data}")
        ])

    async def process(self, state: State) -> Tuple[List[BaseMessage], State]:
        """Score jobs for relevance against resume."""
        if "job_listings" not in state or "resume_data" not in state:
            raise ValueError("Missing job listings or resume data in state")

        scores = {}
        explanations = {}
        
        # Score each job
        for job in state["job_listings"]:
            score_response = await self.llm.apredict_messages(
                self.prompt.format_messages(
                    job_description=job["description"],
                    resume_data=state["resume_data"]
                )
            )
            
            # Parse the scoring response
            scores[job["id"]] = score_response.content
            explanations[job["id"]] = score_response.content

        # Update state with scores
        state["job_scores"] = scores
        state["score_explanations"] = explanations
        state["current_stage"] = "jobs_scored"
        
        return [BaseMessage(content=str(scores))], state