# agents/pitch_generator.py
from typing import Dict, Any

def pitch_generator(state: Dict[str, Any]) -> Dict[str, Any]:
    info = state.get("resume_info") or {}
    top = (state.get("scored_jobs") or [{}])
    best = top[0].get("job") if top else None

    name = info.get("name") or "Candidate"
    skills = ", ".join(info.get("skills") or []) or "relevant experience"
    jobline = f"{best['title']} at {best['company']}" if best else "the role"

    pitch = (
        f"Hi Hiring Team, I'm {name}. I’ve worked extensively with {skills} and I’m excited about "
        f"{jobline}. I believe my background aligns well with your needs and I'd love to discuss how "
        f"I can contribute. Thanks for your consideration."
    )

    return {
        "messages": [
            {"role": "assistant", "content": "Generated a tailored pitch for the top job."},
            {"role": "assistant", "content": f"=== PITCH ===\n{pitch}"},
        ],
        "final_pitch": pitch,
    }
