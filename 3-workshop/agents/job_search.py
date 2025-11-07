from typing import Dict, Any, List

# A more varied (and bigger) mock Singapore job market
MOCK_JOBS: List[Dict[str, Any]] = [
    {
        "title": "Python Backend Engineer",
        "company": "Lion City Tech",
        "location": "Singapore",
        "keywords": ["python", "docker", "aws", "microservices", "sql"],
    },
    {
        "title": "Full-stack Engineer (Angular + Spring Boot)",
        "company": "Harbour Systems",
        "location": "Singapore",
        "keywords": ["angular", "spring boot", "java", "sql", "docker"],
    },
    {
        "title": "Data Engineer",
        "company": "Marina Analytics",
        "location": "Singapore",
        "keywords": ["python", "sql", "aws", "kubernetes", "spark"],
    },
    {
        "title": "Platform Engineer",
        "company": "Cloudy",
        "location": "Singapore",
        "keywords": ["kubernetes", "terraform", "aws", "python", "ci/cd"],
    },
    {
        "title": "Site Reliability Engineer (SRE)",
        "company": "Keppel Digital",
        "location": "Singapore",
        "keywords": ["linux", "kubernetes", "observability", "python", "oncall"],
    },
    {
        "title": "Frontend Engineer (React)",
        "company": "Orchard Labs",
        "location": "Singapore",
        "keywords": ["react", "typescript", "javascript", "testing", "ci"],
    },
    {
        "title": "Mobile Engineer (Flutter)",
        "company": "Bukit Apps",
        "location": "Singapore",
        "keywords": ["flutter", "dart", "firebase", "mobile ci", "ux"],
    },
    {
        "title": "QA Automation Engineer",
        "company": "Marina QA",
        "location": "Singapore",
        "keywords": ["selenium", "cypress", "pytest", "python", "ci/cd"],
    },
    {
        "title": "ML Engineer",
        "company": "Sentosa AI",
        "location": "Singapore",
        "keywords": ["python", "pytorch", "mlops", "docker", "kubernetes"],
    },
    {
        "title": "Backend Engineer (Go)",
        "company": "Bukit Backend",
        "location": "Singapore",
        "keywords": ["golang", "grpc", "docker", "kubernetes", "sql"],
    },
    {
        "title": "Solutions Architect (Java/Spring)",
        "company": "Harbour Enterprise",
        "location": "Singapore",
        "keywords": ["spring", "spring boot", "java", "microservices", "aws"],
    },
    {
        "title": "Full-stack Engineer (Angular/Node)",
        "company": "Jurong Works",
        "location": "Singapore",
        "keywords": ["angular", "nodejs", "typescript", "rest", "sql"],
    },
]

def job_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple keyword match against title + keywords.
    Any-of matching (broader) so we get a realistic pool.
    """
    query_terms = (state.get("job_query") or "").lower().split()

    def matches(job: Dict[str, Any]) -> bool:
        hay = " ".join([job["title"].lower()] + job["keywords"])
        if not query_terms:
            return True
        # any-of so we don't end up with 0 matches when the query is long
        return any(q in hay for q in query_terms)

    jobs: List[Dict[str, Any]] = [j for j in MOCK_JOBS if matches(j)]

    return {
        "messages": [{
            "role": "assistant",
            "content": f"Found {len(jobs)} jobs matching your query."
        }],
        "job_listings": jobs,
    }
