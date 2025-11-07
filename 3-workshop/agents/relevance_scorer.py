from typing import Dict, Any, List, Tuple

def _score(skills: List[str], job_keywords: List[str]) -> int:
    sset = set(s.lower() for s in skills)
    jset = set(k.lower() for k in job_keywords)
    return int(len(sset & jset) * 10)  # 0..100 in steps of 10

def relevance_scorer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume_info") or {}
    skills: List[str] = resume.get("skills") or []
    jobs: List[Dict[str, Any]] = state.get("job_listings") or []

    # score every job and keep the overlap for transparency
    scored: List[Dict[str, Any]] = []
    sset = set(s.lower() for s in skills)

    for j in jobs:
        kws = j.get("keywords", [])
        overlap = sorted(sset & set(k.lower() for k in kws))
        score = int(len(overlap) * 10)
        scored.append({
            **j,
            "score": score,
            "overlap": overlap,
        })

    # sort by score desc, then title for stable order
    scored.sort(key=lambda x: (-x["score"], x["title"]))

    # build a compact “Top 5” user message
    top5 = scored[:5]
    if top5:
        lines = [
            f"{i+1}. {j['title']} @ {j['company']} — {j['score']}/100"
            + (f" (overlap: {', '.join(j['overlap'])})" if j.get("overlap") else "")
            for i, j in enumerate(top5)
        ]
        msg = "Top matches:\n" + "\n".join(lines)
    else:
        msg = "No jobs to score."

    return {
        "messages": [{"role": "assistant", "content": msg}],
        "scored_jobs": scored,  # keep full list for downstream (pitch, etc.)
    }
