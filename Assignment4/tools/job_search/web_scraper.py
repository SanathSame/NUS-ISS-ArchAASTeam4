"""Adapter module to expose the existing web scraper under
`tools.job_search.web_scraper` so callers can import from that path.
"""
from tools.web_scraper import search_job_boards

__all__ = ["search_job_boards"]
