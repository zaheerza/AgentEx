"""
Command-line interface for the multi-agent virtual assistant.
"""

import sys
from typing import Optional

from core.orchestrator import OrchestratorAgent
from agents.research_agent import ResearchAgent
from memory.sql_store import SQLMemoryStore
from config.settings import Settings


class CLI:
    """
    Command-line interface for interacting with the virtual assistant.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the CLI.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Initialize memory
        self.memory = SQLMemoryStore(db_path=settings.db_path)

        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent(
            api_key=settings.anthropic_api_key,
            model=settings.model
        )

        # Register agents
        self._register_agents()

    def _register_agents(self):
        """Register all available agents"""
        # Research Agent
        research_agent = ResearchAgent(
            api_key=self.settings.anthropic_api_key,
            memory_store=self.memory
        )
        self.orchestrator.register_agent(research_agent)

        # Future agents will be registered here:
        # feedback_agent = FeedbackAgent(...)
        # deals_agent = DealsAgent(...)
        # writing_agent = WritingAgent(...)

    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "="*60)
        print("🤖 Virtual Assistant - Multi-Agent System")
        print("="*60)
        print("\nAvailable capabilities:")
        print(self.orchestrator._list_capabilities())
        print("\nCommands:")
        print("  - Type your request naturally")
        print("  - '/stats' - View statistics")
        print("  - '/history' - View saved recommendations")
        print("  - '/clear' - Clear conversation history")
        print("  - '/quit' or '/exit' - Exit the assistant")
        print("\n" + "="*60 + "\n")

    def run(self):
        """Run the interactive CLI"""
        self.print_welcome()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break  # Exit if command returns False
                    continue

                # Process user request
                print("\nAssistant: ", end="", flush=True)
                response = self.orchestrator.handle_input(user_input)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except EOFError:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if self.settings.verbose:
                    import traceback
                    traceback.print_exc()

    def handle_command(self, command: str) -> bool:
        """
        Handle special commands.

        Args:
            command: Command string starting with /

        Returns:
            True to continue, False to exit
        """
        command_lower = command.lower()

        if command_lower in ["/quit", "/exit"]:
            print("\nGoodbye! 👋\n")
            return False

        elif command_lower == "/stats":
            self.show_stats()

        elif command_lower == "/history":
            self.show_history()

        elif command_lower == "/clear":
            self.orchestrator.clear_history()
            print("✅ Conversation history cleared\n")

        elif command_lower == "/help":
            self.print_welcome()

        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: /stats, /history, /clear, /help, /quit\n")

        return True

    def show_stats(self):
        """Show system statistics"""
        print("\n" + "="*60)
        print("📊 System Statistics")
        print("="*60)

        # Memory stats
        mem_stats = self.memory.get_stats()
        print("\n📦 Memory Store:")
        print(f"  Total recommendations: {sum(mem_stats.get('recommendations_by_type', {}).values())}")
        for rec_type, count in mem_stats.get('recommendations_by_type', {}).items():
            print(f"    - {rec_type}: {count}")
        print(f"  Visited: {mem_stats.get('visited', 0)}")
        print(f"  Unvisited: {mem_stats.get('unvisited', 0)}")
        print(f"  Feedback entries: {mem_stats.get('total_feedback', 0)}")
        print(f"  Preferences: {mem_stats.get('total_preferences', 0)}")

        # Orchestrator stats
        orch_stats = self.orchestrator.get_stats()
        print(f"\n🤖 Orchestrator:")
        print(f"  Registered agents: {', '.join(orch_stats['registered_agents'])}")
        print(f"  Conversation length: {orch_stats['conversation_length']} messages")

        print("\n" + "="*60 + "\n")

    def show_history(self):
        """Show saved recommendations"""
        print("\n" + "="*60)
        print("📋 Saved Recommendations")
        print("="*60)

        # Get recommendations from memory
        recommendations = self.memory.get_recommendations(limit=20)

        if not recommendations:
            print("\nNo recommendations saved yet.\n")
            return

        # Group by type
        by_type = {}
        for rec in recommendations:
            rec_type = rec['type']
            if rec_type not in by_type:
                by_type[rec_type] = []
            by_type[rec_type].append(rec)

        # Display
        for rec_type, items in by_type.items():
            print(f"\n{rec_type.capitalize()}s ({len(items)}):")
            for i, item in enumerate(items, 1):
                visited = "✅" if item.get('visited') else "⬜"
                print(f"  {i}. {visited} {item['name']}")
                if item.get('location'):
                    print(f"     Location: {item['location']}")
                if item.get('rating'):
                    print(f"     Rating: {item['rating']}/5.0")

        print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    # Load settings
    settings = Settings()

    # Validate settings
    if not settings.validate():
        sys.exit(1)

    # Create and run CLI
    cli = CLI(settings)
    cli.run()


if __name__ == "__main__":
    main()
