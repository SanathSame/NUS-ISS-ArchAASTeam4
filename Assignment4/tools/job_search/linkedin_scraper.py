"""Adapter module to expose the existing linkedin scraper under
`tools.job_search.linkedin_scraper` so callers can import from that path.
"""
from tools.linkedin_scraper import search_linkedin_jobs

__all__ = ["search_linkedin_jobs"]
