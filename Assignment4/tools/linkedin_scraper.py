"""LinkedIn job search tool using Selenium for web scraping."""
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

async def search_linkedin_jobs(search_criteria: Dict) -> List[Dict]:
    """
    Search LinkedIn for jobs matching the given criteria.
    
    Args:
        search_criteria: Dictionary containing search parameters
            - keywords: List of search terms
            - location: Desired job location
            - experience_level: Required experience level
            - job_type: Full-time, Part-time, etc.
    
    Returns:
        List of job postings with details
    """
    # Initialize webdriver (you'll need to set up proper webdriver configuration)
    driver = webdriver.Chrome()
    
    try:
        # Construct search URL
        base_url = "https://www.linkedin.com/jobs/search/?"
        params = {
            "keywords": " ".join(search_criteria.get("keywords", [])),
            "location": search_criteria.get("location", ""),
            "f_E": search_criteria.get("experience_level", ""),
            "f_JT": search_criteria.get("job_type", "")
        }
        
        # Navigate to search results
        search_url = base_url + "&".join([f"{k}={v}" for k, v in params.items() if v])
        driver.get(search_url)
        
        # Wait for job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
        )
        
        # Extract job listings
        jobs = []
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        for card in job_cards:
            job = {
                "id": card.get_attribute("data-job-id"),
                "title": card.find_element(By.CLASS_NAME, "job-card-list__title").text,
                "company": card.find_element(By.CLASS_NAME, "job-card-container__company-name").text,
                "location": card.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text,
                "link": card.find_element(By.CLASS_NAME, "job-card-list__title").get_attribute("href"),
                "description": get_job_description(driver, card)
            }
            jobs.append(job)
        
        return jobs
    
    finally:
        driver.quit()

def get_job_description(driver, job_card) -> str:
    """Click on job card and extract full description."""
    try:
        job_card.click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-description"))
        )
        description = driver.find_element(By.CLASS_NAME, "jobs-description").text
        return description
    except Exception as e:
        print(f"Error getting job description: {e}")
        return ""