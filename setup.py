"""
Setup script for Agentic Platform
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="agentic-platform",
    version="0.1.0",
    description="An autonomous AI agent framework for building general-purpose agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Agentic Platform Team",
    python_requires=">=3.11,<3.14",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-asyncio>=0.25.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
        ],
        "browser": [
            "playwright>=1.51.0",
        ],
        "sandbox": [
            "docker>=7.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-platform=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
