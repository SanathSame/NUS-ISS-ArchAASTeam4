"""Tools package for JobConnect.

This file makes `tools` a proper package so subpackages like
`tools.job_search` can be imported consistently.
"""

__all__ = [
    "linkedin_scraper",
    "web_scraper",
    "mock_job_platform",
]
