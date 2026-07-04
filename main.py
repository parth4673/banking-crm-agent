"""
Main entry point – seeds the database and launches the Streamlit app.
Can also be used for CLI testing.
"""

import sys
import os
import subprocess

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.seed import seed_database


def main():
    """Seed the database and launch Streamlit."""
    print("🏦 Banking CRM Agent")
    print("=" * 40)

    # Step 1: Seed database
    print("📦 Initializing database...")
    seed_database()
    print("✅ Database ready.\n")

    # Step 2: Launch Streamlit
    print("🚀 Starting Streamlit UI...")
    print("   Open http://localhost:8501 in your browser.\n")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        os.path.join("ui", "app.py"),
        "--server.port", "8501",
        "--server.headless", "true",
    ])


def cli_test():
    """Quick CLI test without Streamlit."""
    from dotenv import load_dotenv
    load_dotenv()

    from agent.agent import BankingCRMAgent

    seed_database()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY in .env file or environment.")
        sys.exit(1)

    agent = BankingCRMAgent(api_key=api_key)

    queries = [
        "Find high-value customers likely to convert for a personal loan this month and generate personalized WhatsApp messages.",
        "Show me product recommendations for customer CUST0003.",
        "Search for customers in Bangalore and score them for credit card conversion.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"📝 Query {i}: {query}")
        print(f"{'='*60}")

        result = agent.run(query)

        print(f"\n🔧 Tools used: {len(result['tool_calls'])}")
        for tc in result["tool_calls"]:
            print(f"   Step {tc['step']}: {tc['tool']}({tc['input']})")

        print(f"\n💬 Response:\n{result['response']}")

        # Reset agent for next independent query
        agent.reset()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        cli_test()
    else:
        main()
