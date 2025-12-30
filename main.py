"""
Main entry point for the Agentic Platform
"""

import argparse
import asyncio

from loguru import logger

from app.agent.platform import PlatformAgent


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Agentic Platform - Autonomous AI Agent")
    parser.add_argument(
        "--prompt",
        type=str,
        help="Task prompt for the agent",
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
        default="PlatformAgent",
        help="Agent name",
    )

    args = parser.parse_args()

    try:
        # Create agent
        logger.info("Initializing agent...")
        agent = await PlatformAgent.create(
            name=args.name,
            max_steps=args.max_steps,
        )

        # Get prompt
        if args.prompt:
            prompt = args.prompt
        else:
            print("\n" + "=" * 60)
            print("Agentic Platform - Autonomous AI Agent")
            print("=" * 60)
            prompt = input("\nEnter your task: ").strip()

        if not prompt:
            logger.warning("No prompt provided")
            print("Please provide a task prompt.")
            return

        # Run agent
        logger.info(f"Starting task: {prompt}")
        print("\nAgent is working...\n")

        response = await agent.run(prompt)

        # Print final response
        print("\n" + "=" * 60)
        print("FINAL RESPONSE")
        print("=" * 60)
        print(response)
        print("=" * 60 + "\n")

        logger.info("Task completed")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\nTask interrupted by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\nError: {str(e)}")
    finally:
        # Cleanup
        if "agent" in locals():
            await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
