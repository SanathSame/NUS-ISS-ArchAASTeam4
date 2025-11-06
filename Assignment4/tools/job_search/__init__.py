"""Job-search related tool adapters.

This package provides thin adapter modules so callers can use
`from tools.job_search.linkedin_scraper import ...` while keeping the
existing scraper implementations at `tools/linkedin_scraper.py` and
`tools/web_scraper.py`.
"""

__all__ = ["linkedin_scraper", "web_scraper"]
