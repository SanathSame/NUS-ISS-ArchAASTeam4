from typing import Any, Dict, List, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from ..state import State
from ..tools.job_search.linkedin_scraper import search_linkedin_jobs
from ..tools.job_search.web_scraper import search_job_boards

class JobSearchAgent:
    """Agent responsible for searching jobs based on resume data."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a job search expert. Your task is to:
            1. Analyze the candidate's resume data
            2. Extract relevant search criteria
            3. Formulate effective search queries
            4. Filter and rank the search results
            Return a list of the most relevant job opportunities."""),
            ("user", "Resume Data: {resume_data}\nSearch Criteria: {search_criteria}")
        ])

    async def process(self, state: State) -> Tuple[List[BaseMessage], State]:
        """Search for relevant jobs based on resume data."""
        if "resume_data" not in state:
            raise ValueError("Resume data not found in state")

        # Generate search criteria from resume data
        search_response = await self.llm.apredict_messages(
            self.prompt.format_messages(
                resume_data=state["resume_data"],
                search_criteria=state.get("search_criteria", {})
            )
        )

        # Search for jobs using multiple sources
        linkedin_jobs = await search_linkedin_jobs(search_response.content)
        web_jobs = await search_job_boards(search_response.content)

        # Combine and deduplicate job listings
        all_jobs = linkedin_jobs + web_jobs
        
        # Update state with job listings
        state["job_listings"] = all_jobs
        state["current_stage"] = "jobs_found"
        
        return [search_response], state