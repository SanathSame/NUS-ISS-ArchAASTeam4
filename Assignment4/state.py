"""State management for the JobConnect system."""
from typing import TypedDict, List, Dict, Optional
from enum import Enum

class JobSearchStage(Enum):
    """Enum for tracking the current stage of the job search workflow."""
    INIT = "init"
    RESUME_PARSED = "resume_parsed"
    JOBS_SEARCHED = "jobs_searched"
    JOBS_SCORED = "jobs_scored"
    CONTENT_GENERATED = "content_generated"

class PersonalInfo(TypedDict):
    """Structure for personal information from resume."""
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]

class Education(TypedDict):
    """Structure for education information."""
    degree: str
    institution: str
    start_date: str
    end_date: Optional[str]
    gpa: Optional[float]
    achievements: List[str]

class WorkExperience(TypedDict):
    """Structure for work experience information."""
    company: str
    position: str
    start_date: str
    end_date: Optional[str]
    description: List[str]
    achievements: List[str]

class Project(TypedDict):
    """Structure for project information."""
    name: str
    description: str
    technologies: List[str]
    url: Optional[str]

class ResumeData(TypedDict):
    """Structure for parsed resume data."""
    personal_info: PersonalInfo
    education: List[Education]
    experience: List[WorkExperience]
    skills: List[str]
    projects: List[Project]

class JobPosting(TypedDict):
    """Structure for job posting information."""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    salary_range: Optional[str]
    posting_date: str
    source: str

class JobScore(TypedDict):
    """Structure for job matching scores."""
    total_score: float
    skill_score: float
    experience_score: float
    qualitative_score: float
    explanation: str

class JobSearchState(TypedDict):
    """Overall state of the JobConnect system."""
    stage: JobSearchStage
    resume_data: Optional[ResumeData]
    search_query: Optional[Dict]
    job_listings: List[JobPosting]
    relevance_scores: Dict[str, JobScore]
    generated_content: Dict[str, str]
    messages: List[Dict]
    error: Optional[str]

def create_initial_state() -> JobSearchState:
    """Create initial state for the JobConnect system."""
    return JobSearchState(
        stage=JobSearchStage.INIT,
        resume_data=None,
        search_query=None,
        job_listings=[],
        relevance_scores={},
        generated_content={},
        messages=[],
        error=None
    )


# Backwards compatibility: some code (copied from the workshop) expects a
# `State` type exported from this module. Provide a simple alias so imports
# like `from state import State` continue to work.
State = JobSearchState