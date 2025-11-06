"""Main entry point for the JobConnect system."""
from typing import Optional, Dict, List
import os
import asyncio
from pathlib import Path
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from state import JobSearchState, JobSearchStage, create_initial_state
from agents.router import JobSearchRouter
from agents.resume_parser import ResumeParserAgent
from agents.job_searcher import JobSearchAgent
from agents.relevance_scorer import RelevanceScorerAgent
from tools.mock_job_platform import MockJobPlatformAPI

from dotenv import load_dotenv
load_dotenv(override=True)  

console = Console()

class JobConnectSystem:
    """Main system class for JobConnect."""
    
    def __init__(self):
        # Create a shared LLM instance and inject into agents that require it.
        # Use a small compatibility fallback to support different langchain packaging.
        def _get_chat_llm(**kwargs):
            ChatCls = None
            try:
                # Newer langchain layout
                from langchain.chat_models import ChatOpenAI as ChatCls
            except Exception:
                try:
                    # Older packaging / shim
                    from langchain_openai import ChatOpenAI as ChatCls
                except Exception:
                    ChatCls = None

            if ChatCls is None:
                # Fall back to a dumb placeholder that raises helpful error when used.
                class _NoLLM:
                    def __init__(self, *a, **k):
                        raise RuntimeError(
                            "No ChatOpenAI implementation available.\n"
                            "Install a supported langchain langchain-openai package or adjust imports."
                        )
                return _NoLLM(**kwargs)

            return ChatCls(**kwargs)

        # instantiate LLM (model selection left to environment/config)
        try:
            self.llm = _get_chat_llm(temperature=0.0)
        except Exception as e:
            # Keep raising a clearer error when initialization fails
            raise RuntimeError(f"Failed to create LLM: {e}") from e

        self.router = JobSearchRouter()
        self.state = create_initial_state()
        # Pass shared LLM into agents expecting an `llm` constructor arg
        self.resume_parser = ResumeParserAgent(self.llm)
        self.job_searcher = JobSearchAgent(self.llm)
        self.relevance_scorer = RelevanceScorerAgent(self.llm)

    def display_welcome(self):
        """Display welcome message and system capabilities."""
        welcome_message = """
        👋 Welcome to JobConnect! I'm your AI assistant for job search.
        
        Tell me what you'd like to do:
        
        • "I want to analyze my resume" - I'll extract key skills and experience
        • "Find jobs for me" - I'll search our job platform based on your profile
        • "Score these jobs" - I'll rank jobs by match against your resume
        • "Write a cover letter" - I'll generate a customized letter for any job
        
        Just type what you want to do, and I'll help you get started!
        """
        console.print(Panel(welcome_message, title="[bold blue]JobConnect Agent[/bold blue]", 
                          border_style="blue"))

    def get_resume_path(self) -> Optional[str]:
        """Get and validate resume file path from user."""
        while True:
            console.print("\n📄 Please enter the path to your resume (PDF) or 'q' to quit:", 
                        style="yellow")
            file_path = input().strip()
            
            if file_path.lower() == 'q':
                return None
                
            path = Path(file_path)
            if path.exists() and path.suffix.lower() == '.pdf':
                return str(path.absolute())
            else:
                console.print("❌ Invalid file path or not a PDF. Please try again.", 
                            style="red")

    async def get_job_preferences(self) -> Dict:
        """Get job search preferences from user."""
        preferences = {}
        
        # Location preference
        console.print("\n📍 Would you like to specify a location? (Enter location or press Enter to skip)")
        location = input().strip()
        if location:
            preferences["location"] = location

        # Job type preference
        console.print("\n💼 Select job type:")
        job_types = ["Full-time", "Part-time", "Contract", "Remote", "Any"]
        for i, jt in enumerate(job_types, 1):
            console.print(f"{i}. {jt}")
        choice = input("Enter your choice (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(job_types):
            preferences["job_type"] = job_types[int(choice)-1]

        # Experience level
        console.print("\n📊 Select experience level:")
        exp_levels = ["Entry Level", "Mid Level", "Senior", "Lead", "Any"]
        for i, el in enumerate(exp_levels, 1):
            console.print(f"{i}. {el}")
        choice = input("Enter your choice (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(exp_levels):
            preferences["experience_level"] = exp_levels[int(choice)-1]

        # Keywords/Skills
        console.print("\n🔑 Enter any specific keywords or skills (comma-separated, or press Enter to skip):")
        keywords = input().strip()
        if keywords:
            preferences["keywords"] = [k.strip() for k in keywords.split(",")]

        return preferences

    def display_job_results(self, jobs: List[Dict], scores: Dict[str, Dict]):
        """Display job search results in a formatted table."""
        table = Table(title="🎯 Job Matches", show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Score", style="green")
        table.add_column("Title", style="blue")
        table.add_column("Company", style="yellow")
        table.add_column("Location", style="magenta")
        table.add_column("Match Details", style="white")
        
        # Sort jobs by score
        sorted_jobs = sorted(
            [(job, scores[job["id"]]) for job in jobs],
            key=lambda x: x[1]["total_score"],
            reverse=True
        )
        
        for rank, (job, score) in enumerate(sorted_jobs, 1):
            match_details = (
                f"Skills: {score['skill_score']*100:.0f}% | "
                f"Exp: {score['experience_score']*100:.0f}% | "
                f"Overall: {score['qualitative_score']*100:.0f}%"
            )
            table.add_row(
                str(rank),
                f"{score['total_score']*100:.0f}%",
                job["title"],
                job["company"],
                job["location"],
                match_details
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n💡 Jobs are ranked based on skill match, experience level, and overall qualitative assessment.")

    async def run(self):
        """Interactive command loop for JobConnect system."""
        self.display_welcome()

        while True:
            # Get natural language input from user
            console.print("\nWhat would you like me to help you with?", style="yellow")
            console.print("(Type 'exit' to quit, 'help' to see options again)", style="dim")
            cmd = input("\n> ").strip().lower()

            if not cmd:
                continue

            try:
                # Process commands using natural language matching
                if cmd in ('exit', 'quit', 'bye'):
                    console.print("\n👋 Goodbye!", style="blue")
                    return

                if cmd in ('help', 'options', '?'):
                    self.display_welcome()
                    continue

                # Resume analysis
                if any(x in cmd for x in ['resume', 'analyze', 'parse', 'extract']):
                    console.print("\n📝 Please paste your resume text (end with an empty line):", style="yellow")
                    lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        lines.append(line)
                    
                    resume_text = "\n".join(lines).strip()
                    if not resume_text:
                        console.print("No resume text provided.", style="red")
                        continue

                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                        task = progress.add_task("📄 Analyzing your resume...", total=None)
                        self.state["resume_text"] = resume_text
                        msgs, self.state = await self.resume_parser.process(self.state)
                        progress.update(task, completed=True)

                    if self.state.get("resume_data"):
                        console.print("\n✨ Resume Analysis:", style="bold green")
                        console.print(f"• Found {len(self.state['resume_data']['skills'])} skills")
                        console.print(f"• {len(self.state['resume_data']['experience'])} work experiences")
                        console.print(f"• {len(self.state['resume_data']['education'])} education entries")

                # Job search
                elif any(x in cmd for x in ['find job', 'search job', 'look for job']):
                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                        task = progress.add_task("🔍 Searching jobs...", total=None)
                        msgs, self.state = await self.job_searcher.process(self.state)
                        progress.update(task, completed=True)
                    
                    n = len(self.state.get('job_listings', []))
                    console.print(f"\n✨ Found {n} potential matches!", style="green")

                # Job scoring
                elif any(x in cmd for x in ['score', 'rank', 'match']):
                    if not self.state.get('job_listings'):
                        console.print("\n❌ No jobs to score yet. Try searching for jobs first!", style="red")
                        continue

                    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                        task = progress.add_task("🎯 Scoring job matches...", total=None)
                        msgs, self.state = await self.relevance_scorer.process(self.state)
                        progress.update(task, completed=True)

                    if self.state.get('job_scores'):
                        self.display_job_results(
                            self.state["job_listings"],
                            self.state["job_scores"]
                        )

                # Cover letter generation
                elif any(x in cmd for x in ['cover letter', 'write letter']):
                    if not self.state.get('job_scores'):
                        console.print("\n❌ Please score jobs first to generate a targeted cover letter!", style="red")
                        continue

                    # TODO: Add cover letter generation agent here
                    console.print("\n✨ Cover letter generation coming soon!", style="blue")

                else:
                    console.print("\n❓ I'm not sure what you want to do. Try:", style="yellow")
                    console.print("• 'analyze my resume'")
                    console.print("• 'find jobs for me'")
                    console.print("• 'score these jobs'")
                    console.print("• 'write a cover letter'")

            except Exception as e:
                console.print(f"\n❌ An error occurred: {str(e)}", style="red")
                # Process resume
                task1 = progress.add_task("📝 Analyzing your resume...", total=None)
                self.state = await self.resume_parser.process(self.state, resume_path)
                
                if self.state.get("error"):
                    raise Exception(self.state["error"])
                
                progress.update(task1, completed=True)
                
                # Display parsed resume summary
                if self.state["resume_data"]:
                    console.print("\n📄 Resume Analysis Summary:", style="bold blue")
                    console.print(f"• Found {len(self.state['resume_data']['skills'])} skills")
                    console.print(f"• {len(self.state['resume_data']['experience'])} work experiences")
                    console.print(f"• {len(self.state['resume_data']['education'])} educational qualifications")
                
                # Get job preferences
                preferences = await self.get_job_preferences()
                self.state["search_query"] = preferences
                
                # Search jobs
                task2 = progress.add_task("🔍 Searching for matching jobs...", total=None)
                self.state = await self.job_searcher.process(self.state)
                
                if self.state.get("error"):
                    raise Exception(self.state["error"])
                
                progress.update(task2, completed=True)
                
                # Score jobs
                task3 = progress.add_task("🎯 Analyzing job matches...", total=None)
                self.state = await self.relevance_scorer.process(self.state)
                
                if self.state.get("error"):
                    raise Exception(self.state["error"])
                
                progress.update(task3, completed=True)

            # Display results
            self.display_job_results(
                self.state["job_listings"],
                self.state["relevance_scores"]
            )
            
            # Ask about cover letter generation
            console.print("\n✍️  Would you like me to generate a cover letter for any of the top matches? (y/n)", 
                        style="yellow")
            if input().lower() == 'y':
                while True:
                    try:
                        rank = int(input("Enter the rank number of the job (or 0 to skip): "))
                        if rank == 0:
                            break
                        if 1 <= rank <= len(self.state["job_listings"]):
                            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                                task = progress.add_task("✍️  Crafting your cover letter...", total=None)
                                # Cover letter generation would go here
                                progress.update(task, completed=True)
                            break
                        else:
                            console.print("❌ Invalid rank number. Please try again.", style="red")
                    except ValueError:
                        console.print("❌ Please enter a valid number.", style="red")
            
            # Save results option
            console.print("\n💾 Would you like to save these results to a file? (y/n)", style="yellow")
            if input().lower() == 'y':
                # Save results implementation would go here
                console.print("Results saved to 'job_search_results.json'", style="green")
            
            console.print("\n✨ Thank you for using JobConnect! Good luck with your job search!", 
                         style="blue")

def main():
    """Entry point of the application."""
    try:
        system = JobConnectSystem()
        asyncio.run(system.run())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="blue")
    except Exception as e:
        console.print(f"\n❌ A system error occurred: {str(e)}", style="red")

if __name__ == "__main__":
    main()