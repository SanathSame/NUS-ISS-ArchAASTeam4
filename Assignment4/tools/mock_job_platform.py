"""Mock Job Platform API client."""
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta

class MockJobPlatformAPI:
    """Mock API client for a job platform."""
    
    def __init__(self):
        self._jobs_db = self._initialize_mock_jobs()
    
    def _initialize_mock_jobs(self) -> List[Dict]:
        """Initialize mock job database."""
        job_titles = [
            "Software Engineer", "Data Scientist", "Product Manager",
            "DevOps Engineer", "Full Stack Developer", "AI Engineer",
            "Cloud Architect", "Machine Learning Engineer"
        ]
        
        companies = [
            "TechCorp", "DataInnovate", "CloudScale",
            "AIFuture", "DevPro Solutions", "InnovateSG"
        ]
        
        locations = ["Singapore", "Remote"]
        
        skills = [
            "Python", "Java", "JavaScript", "React", "Node.js",
            "AWS", "Docker", "Kubernetes", "TensorFlow", "PyTorch"
        ]
        
        jobs = []
        for i in range(50):  # Generate 50 mock jobs
            # Random posting date within last 30 days
            posting_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Random salary range
            base_salary = random.randint(5, 15) * 1000
            max_salary = base_salary + random.randint(2, 8) * 1000
            
            # Random required skills (3-6 skills)
            required_skills = random.sample(skills, random.randint(3, 6))
            
            job = {
                "id": f"JOB-{i+1:04d}",
                "title": random.choice(job_titles),
                "company": random.choice(companies),
                "location": random.choice(locations),
                "description": self._generate_description(required_skills),
                "requirements": required_skills,
                "salary_range": f"${base_salary:,} - ${max_salary:,}",
                "posting_date": posting_date.strftime("%Y-%m-%d"),
                "source": "MockJobPlatform"
            }
            jobs.append(job)
        
        return jobs
    
    def _generate_description(self, required_skills: List[str]) -> str:
        """Generate a mock job description."""
        return f"""
We are looking for a talented professional to join our team.

Required Skills:
{', '.join(required_skills)}

Responsibilities:
- Design and implement scalable solutions
- Collaborate with cross-functional teams
- Participate in code reviews and technical discussions
- Mentor junior team members

Benefits:
- Competitive salary
- Flexible working hours
- Professional development opportunities
- Health insurance
"""

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        skills: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for jobs based on query and filters.
        
        Args:
            query: Search query string
            location: Optional location filter
            skills: Optional list of required skills
            max_results: Maximum number of results to return
            
        Returns:
            List of matching job postings
        """
        # Convert query to lowercase for case-insensitive search
        query = query.lower()
        matching_jobs = []
        
        for job in self._jobs_db:
            # Check if query matches title or description
            if query in job["title"].lower() or query in job["description"].lower():
                # Apply location filter if specified
                if location and location.lower() != job["location"].lower():
                    continue
                    
                # Apply skills filter if specified
                if skills:
                    if not all(skill in job["requirements"] for skill in skills):
                        continue
                
                matching_jobs.append(job)
                
                if len(matching_jobs) >= max_results:
                    break
        
        return matching_jobs

    async def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Get detailed information for a specific job."""
        for job in self._jobs_db:
            if job["id"] == job_id:
                return job
        return None