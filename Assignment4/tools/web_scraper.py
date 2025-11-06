"""General web scraper for job boards using requests and BeautifulSoup."""
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import json

async def search_job_boards(search_criteria: Dict) -> List[Dict]:
    """
    Search multiple job boards for matching positions.
    
    Args:
        search_criteria: Dictionary containing search parameters
            - keywords: List of search terms
            - location: Desired job location
            - experience_level: Required experience level
            - job_type: Full-time, Part-time, etc.
    
    Returns:
        List of job postings with details
    """
    # List of job boards to search
    job_boards = [
        {
            "name": "Indeed",
            "url": "https://www.indeed.com/jobs",
            "parser": parse_indeed_jobs
        },
        {
            "name": "Glassdoor",
            "url": "https://www.glassdoor.com/Job/jobs.htm",
            "parser": parse_glassdoor_jobs
        }
        # Add more job boards as needed
    ]
    
    all_jobs = []
    
    # Search each job board
    for board in job_boards:
        try:
            jobs = await search_job_board(board, search_criteria)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error searching {board['name']}: {e}")
    
    return all_jobs

async def search_job_board(board: Dict, search_criteria: Dict) -> List[Dict]:
    """Search a specific job board."""
    # Construct search URL with parameters
    params = {
        "q": " ".join(search_criteria.get("keywords", [])),
        "l": search_criteria.get("location", ""),
        # Add other parameters based on the job board
    }
    
    # Make request
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)"
    }
    response = requests.get(board["url"], params=params, headers=headers)
    
    if response.status_code == 200:
        # Parse response using board-specific parser
        return await board["parser"](response.text)
    else:
        print(f"Error {response.status_code} from {board['name']}")
        return []

async def parse_indeed_jobs(html: str) -> List[Dict]:
    """Parse Indeed job listings."""
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    
    # Find all job cards
    for card in soup.find_all("div", class_="job_seen_beacon"):
        try:
            job = {
                "id": card.get("data-jk", ""),
                "title": card.find("h2", class_="jobTitle").text.strip(),
                "company": card.find("span", class_="companyName").text.strip(),
                "location": card.find("div", class_="companyLocation").text.strip(),
                "description": card.find("div", class_="job-snippet").text.strip(),
                "source": "Indeed"
            }
            jobs.append(job)
        except Exception as e:
            print(f"Error parsing Indeed job: {e}")
    
    return jobs

async def parse_glassdoor_jobs(html: str) -> List[Dict]:
    """Parse Glassdoor job listings."""
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    
    # Find all job cards
    for card in soup.find_all("li", class_="react-job-listing"):
        try:
            job = {
                "id": card.get("data-id", ""),
                "title": card.find("a", class_="jobLink").text.strip(),
                "company": card.find("div", class_="jobHeader").text.strip(),
                "location": card.find("span", class_="loc").text.strip(),
                "description": card.find("div", class_="jobDescriptionContent").text.strip(),
                "source": "Glassdoor"
            }
            jobs.append(job)
        except Exception as e:
            print(f"Error parsing Glassdoor job: {e}")
    
    return jobs