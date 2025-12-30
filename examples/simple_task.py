"""
Simple example of using the Agentic Platform
"""

import asyncio

from app.agent.platform import PlatformAgent


async def main():
    # Create an agent
    agent = await PlatformAgent.create(
        name="SimpleAgent",
        max_steps=10,
    )

    # Run a simple task
    prompt = "What is the current date and time?"
    response = await agent.run(prompt)

    print(f"Response: {response}")

    # Cleanup
    await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
