"""
Main entry point for the Agentic Platform
"""

import argparse
import asyncio

from loguru import logger

from app.agent import (
    PlatformAgent,
    BrowserAgent,
    DataAnalysisAgent,
    MCPAgent,
    FullStackShipAgent,
    TestAgent,
)


# Available agent types
AGENT_TYPES = {
    "platform": PlatformAgent,
    "browser": BrowserAgent,
    "data": DataAnalysisAgent,
    "mcp": MCPAgent,
    "ship": FullStackShipAgent,
    "test": TestAgent,
}


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Agentic Platform - Autonomous AI Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent Types:
  platform      General-purpose agent with all tools (default)
  browser       Specialized browser automation agent
  data          Data analysis and visualization agent
  mcp           Agent with Model Context Protocol support
  ship          FullStack SaaS app builder (Supabase + Stripe + Deploy)
  test          Testing and validation agent (checks all components)

Examples:
  python main.py --prompt "Search for Python news"
  python main.py --agent browser --prompt "Go to google.com and search for AI"
  python main.py --agent data --prompt "Analyze data.csv and create visualizations"
  python main.py --agent ship --prompt "Build a SaaS app for project management"
  python main.py --agent test --prompt "Run a comprehensive health check"
        """,
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Task prompt for the agent",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="platform",
        choices=list(AGENT_TYPES.keys()),
        help="Type of agent to use (default: platform)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum number of execution steps",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Custom agent name (optional)",
    )

    args = parser.parse_args()

    try:
        # Get agent class
        agent_class = AGENT_TYPES[args.agent]

        # Create agent
        logger.info(f"Initializing {args.agent} agent...")

        agent_kwargs = {"max_steps": args.max_steps}
        if args.name:
            agent_kwargs["name"] = args.name

        agent = await agent_class.create(**agent_kwargs)

        # Get prompt
        if args.prompt:
            prompt = args.prompt
        else:
            print("\n" + "=" * 70)
            print(" " * 15 + "AGENTIC PLATFORM - AI Agent Framework")
            print("=" * 70)
            print(f"\nAgent Type: {args.agent.upper()}")
            print(f"Agent Name: {agent.name}")
            print(f"Max Steps: {args.max_steps}")
            print(f"Available Tools: {len(agent.tool_collection.tools)}")
            print("\n" + "-" * 70)
            prompt = input("\nEnter your task: ").strip()

        if not prompt:
            logger.warning("No prompt provided")
            print("Please provide a task prompt.")
            return

        # Run agent
        logger.info(f"Starting task with {args.agent} agent: {prompt}")
        print("\n" + "=" * 70)
        print("AGENT IS WORKING...")
        print("=" * 70 + "\n")

        response = await agent.run(prompt)

        # Print final response
        print("\n" + "=" * 70)
        print(" " * 25 + "FINAL RESPONSE")
        print("=" * 70)
        print(response)
        print("=" * 70)
        print(f"\nSteps used: {agent.current_step}/{args.max_steps}")
        print(f"Agent state: {agent.state.value}")
        print("=" * 70 + "\n")

        logger.info("Task completed")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\nTask interrupted by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\nError: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        if "agent" in locals():
            await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
