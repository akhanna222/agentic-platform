"""
Example demonstrating file operations
"""

import asyncio

from app.agent.platform import PlatformAgent


async def main():
    agent = await PlatformAgent.create(
        name="FileAgent",
        max_steps=15,
    )

    # Task involving file operations
    prompt = """
    Create a file called 'test.txt' with the text 'Hello, World!' and then read it back to verify.
    """

    response = await agent.run(prompt)
    print(f"Response: {response}")

    await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
