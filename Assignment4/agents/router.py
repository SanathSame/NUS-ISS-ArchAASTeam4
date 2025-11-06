"""Router for coordinating job search workflow."""
from typing import Tuple, Dict
from langchain_openai import ChatOpenAI
from state import JobSearchState, JobSearchStage

class JobSearchRouter:
    """
    Router that coordinates the job search workflow and manages tool permissions.
    Each agent has specific tool permissions:
    
    1. Resume Parser:
    - Access to LLM for parsing
    - No access to job platform API
    
    2. Job Searcher:
    - Access to mock job platform API only
    - No access to LLM
    
    3. Relevance Scorer:
    - Access to LLM for scoring
    - No access to job platform API
    
    4. Content Generator:
    - Access to LLM for generation
    - Access to specific templates
    """
    
    def __init__(self):
        self.llm = ChatOpenAI()  # For agents that need LLM access
    
    def route(self, state: JobSearchState) -> Tuple[str, Dict]:
        """
        Determine next agent based on current state.
        
        Returns:
            Tuple of (next_agent_name, agent_config)
        """
        current_stage = state["stage"]
        
        if current_stage == JobSearchStage.INIT:
            if not state["resume_data"]:
                return "resume_parser", {"use_llm": True}
                
        elif current_stage == JobSearchStage.RESUME_PARSED:
            return "job_searcher", {"use_job_api": True}
            
        elif current_stage == JobSearchStage.JOBS_SEARCHED:
            if state["job_listings"]:
                return "relevance_scorer", {"use_llm": True}
                
        elif current_stage == JobSearchStage.JOBS_SCORED:
            return "content_generator", {
                "use_llm": True,
                "use_templates": True
            }
        
        return "end", {}
    
    def validate_tool_access(self, agent_name: str, tool_name: str) -> bool:
        """
        Validate if an agent has permission to use a specific tool.
        
        Args:
            agent_name: Name of the agent requesting tool access
            tool_name: Name of the tool being requested
            
        Returns:
            Boolean indicating if access is allowed
        """
        permissions = {
            "resume_parser": ["llm"],
            "job_searcher": ["job_platform_api"],
            "relevance_scorer": ["llm"],
            "content_generator": ["llm", "templates"]
        }
        
        allowed_tools = permissions.get(agent_name, [])
        return tool_name in allowed_tools