# main.py
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import random

from state import State
from nodes import (
    human_node,
    check_exit_condition,
    coordinator_routing,
    participant_node,
    summarizer_node,
)
from agents.coordinator import coordinator


# 10 realistic resume/query pairs (keep them short & tech-keyword friendly)
RESUME_SCENARIOS = [
    (
        "Senior engineer, 5 years with Python, Angular, Spring Boot, SQL, AWS, Docker.",
        "python angular spring singapore"
    ),
    (
        "Backend developer, 6+ years in Java, Spring Boot, Kafka, PostgreSQL, Redis, AWS ECS.",
        "java spring boot kafka postgres redis singapore"
    ),
    (
        "Full-stack engineer with 4 years in React, Node.js, Express, MongoDB, CI/CD, Docker.",
        "react node express mongodb docker singapore"
    ),
    (
        "Data engineer, 5 years in Python, Spark, Airflow, AWS Glue, S3, Redshift, SQL.",
        "data engineer python spark airflow redshift singapore"
    ),
    (
        "DevOps engineer, 7 years in Kubernetes, Terraform, AWS, GitLab CI, Prometheus, Grafana.",
        "devops kubernetes terraform aws gitlab ci singapore"
    ),
    (
        "Frontend engineer, 3 years in Angular, RxJS, TypeScript, Tailwind, Jest, Cypress.",
        "angular rxjs typescript jest cypress singapore"
    ),
    (
        "Mobile developer, 4 years in Android (Kotlin), Jetpack, Retrofit, Firebase, CI/CD.",
        "android kotlin jetpack retrofit firebase singapore"
    ),
    (
        "QA automation engineer, 5 years with Selenium, Playwright, Java, TestNG, REST Assured.",
        "qa automation selenium playwright java testng singapore"
    ),
    (
        "ML engineer, 3 years in Python, PyTorch, Transformers, FastAPI, MLflow, AWS SageMaker.",
        "ml engineer pytorch transformers fastapi sagemaker singapore"
    ),
    (
        "Platform engineer, 6 years in Go, Kubernetes, Helm, Istio, ArgoCD, Observability.",
        "platform engineer go kubernetes helm istio argocd singapore"
    ),
]


def build_graph():
    builder = StateGraph(State)
    builder.add_node("human", human_node)
    builder.add_node("coordinator", coordinator)
    builder.add_node("participant", participant_node)
    builder.add_node("summarizer", summarizer_node)

    builder.add_edge(START, "human")
    builder.add_conditional_edges(
        "human", check_exit_condition, {"summarizer": "summarizer", "coordinator": "coordinator"}
    )
    builder.add_conditional_edges(
        "coordinator", coordinator_routing, {"participant": "participant", "human": "human"}
    )
    builder.add_edge("participant", "coordinator")
    builder.add_edge("summarizer", END)
    return builder.compile()


def main():
    load_dotenv(override=True)
    print("=== SINGAPORE JOB SEARCH DEMO ===")
    print("Type 'exit' to end.\n")

    graph = build_graph()
    print(graph.get_graph().draw_ascii())

    # Pick a scenario at random (set PY_DEMO_SEED for reproducibility if needed)
    seed_env = None  # change to an int or read from env if you want deterministic runs
    if seed_env is not None:
        random.seed(seed_env)

    resume_text, job_query = random.choice(RESUME_SCENARIOS)
    print("\n[DEMO] Using scenario:")
    print(f"       Resume: {resume_text}")
    print(f"       Query : {job_query}\n")

    initial_state = State(
        messages=[],
        volley_msg_left=8,
        next_agent=None,
        resume_text=resume_text,
        job_query=job_query,
        stage_idx=0,  # start at the first agent
    )

    try:
        graph.invoke(initial_state, config={"recursion_limit": 100})
    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ending conversation...")


if __name__ == "__main__":
    main()
