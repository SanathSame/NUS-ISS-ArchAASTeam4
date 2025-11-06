from typing import Any, Dict, List, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from ..state import State

class ResumeParserAgent:
    """Agent responsible for parsing resume content and extracting structured data."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume parser. Your task is to extract key information from resumes into a structured format.
            Extract the following information:
            - Personal Info (name, contact, location)
            - Education (degrees, institutions, dates)
            - Work Experience (companies, positions, dates, key achievements)
            - Skills (technical skills, soft skills)
            - Projects (names, descriptions, technologies used)
            Format the output as a detailed JSON structure."""),
            ("user", "{resume_text}")
        ])

    async def process(self, state: State) -> Tuple[List[BaseMessage], State]:
        """Process the resume and extract structured information."""
        if "resume_text" not in state:
            raise ValueError("Resume text not found in state")

        # Generate structured resume data
        parsed_data = await self.llm.apredict_messages(
            self.prompt.format_messages(resume_text=state["resume_text"])
        )

        # Update state with parsed resume data
        state["resume_data"] = parsed_data.content
        state["current_stage"] = "resume_parsed"
        
        return [parsed_data], state