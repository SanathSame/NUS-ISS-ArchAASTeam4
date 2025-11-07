# Job Connect Demo (LangGraph Multi-Agent)
 
A hands-on demonstration of a **multi-agent job search assistant**, built using **LangGraph** and **LangChain**, that parses resumes, finds relevant jobs, scores them, and generates a personalized job pitch; all in one conversational flow.
 
## Overview
 
This project simulates between user and multiple collaborating AI agents, each performing a distinct step in the job search pipeline:
 
| Agent | Responsibility |
|-------|----------------|
| **Human Node** | Accepts user input (e.g., greetings, exit command). |
| **Resume Parser** | Extracts skills and experience from a given resume text. |
| **Job Search** | Searches mock job listings that match extracted skills. |
| **Relevance Scorer** | Scores and ranks top jobs by skill overlap. |
| **Pitch Generator** | Crafts a tailored pitch for the best-matched role. |
| **Summarizer** | Summarizes the overall agent conversation and outcomes. |
 
Each run randomly selects one of 10 resume/job-query pairs for variety and realism.
 
---
 
## Architecture
 
┌──────────┐
│ START │
└────┬─────┘
│
▼
┌──────────┐ ┌────────────┐ ┌───────────────┐
│ Human │──►│ Coordinator │──►│ Participant │
└──────────┘ └────────────┘ └───────────────┘
│
▼
┌──────────────┐
│ Summarizer │
└──────────────┘
 
 
- **`State`** tracks progress: messages, agent outputs, volley count, and stage index.  
- **`Coordinator`** decides which agent runs next.  
- **`Participant`** calls the corresponding agent module.  
- **Nodes** define LangGraph node logic and transitions.  
- **`main.py`** orchestrates the demo flow.
 
---
 
## Setup Instructions
 
### 1. Clone & Install Dependencies
 
git clone https://github.com/SanathSame/NUS-ISS-ArchAASTeam4.git.
 
cd 3-workshop
uv sync
 
--
 
## 2. Setup Environment
 
OPENAI_API_KEY=your_openai_key_here
 
 
## 3. Run the Demo
 
uv run python main.py
 
You’ll see the ASCII graph and a randomly chosen resume scenario:
 
[DEMO] Using scenario:
       Resume: DevOps engineer, 7 years in Kubernetes, Terraform, AWS, GitLab CI, Prometheus, Grafana.
       Query : devops kubernetes terraform aws gitlab ci singapore
 
 
## 4. Example Output
[COORDINATOR] Next agent: resume_parser
[RESUME] Parsed resume.
Parsed resume. Skills: aws, git, kubernetes. Experience: 7 yrs.
 
[JOBS] Fetched job listings.
Found 10 jobs matching your query.
 
[SCORE] Scored job listings.
Top matches:
1. Platform Engineer @ Cloudy — 20/100 (overlap: aws, kubernetes)
2. Data Engineer @ Marina Analytics — 20/100 (overlap: aws, kubernetes)
...
 
[PITCH] Generated pitch.
=== PITCH ===
Hi Hiring Team, I'm Candidate. I’ve worked extensively with aws, git, kubernetes and I’m excited about Platform Engineer at Cloudy...
 
## 5. Folder Structure
3-workshop/
├── agents/
│   ├── __init__.py
│   ├── coordinator.py
│   ├── participant.py
│   ├── resume_parser.py
│   ├── job_search.py
│   ├── relevance_scorer.py
│   ├── pitch_generator.py
│   └── summarizer.py
├── nodes.py
├── state.py
├── main.py
├── utils.py
└── README.md
 
## 5. Future Enhancement
- Integrate live job APIs (LinkedIn, MyCareersFuture, Indeed)
- Add resume upload + LLM parsing using embeddings
- Extend multi-turn conversations for job filtering
- Include evaluation metrics for agent accuracy
- Build a Streamlit / Gradio web UI
 
 
## 6. Credits
 
Developed for NUS-ISS ArchAAS Workshop
Author: Hany, Sanath, Anastasia, Ke An (Team 4)
Purpose: Multi-Agent Reasoning with LangGraph