# Contributing to Agentic Platform

Thank you for your interest in contributing to the Agentic Platform! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/agentic-platform.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install dev dependencies: `pip install pytest pytest-asyncio black ruff`

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Add type hints where appropriate

### 3. Test Your Changes

```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/test_schema.py

# Run with coverage
pytest --cov=app tests/
```

### 4. Format and Lint

```bash
# Format code with black
black app/ main.py tests/

# Lint with ruff
ruff check app/ main.py tests/

# Fix auto-fixable issues
ruff check --fix app/ main.py tests/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "Add feature: description of your changes"
```

Follow these commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests when relevant

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Python Style Guide

- Follow PEP 8
- Use meaningful variable names
- Maximum line length: 100 characters
- Use type hints
- Write docstrings for all public functions and classes

### Example

```python
from typing import Optional


def calculate_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Calculate the number of tokens in text.

    Args:
        text: The text to tokenize
        model: The model to use for tokenization

    Returns:
        The number of tokens

    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")

    # Implementation here
    pass
```

## Adding New Tools

To add a new tool:

1. Create a new class in `app/tools/builtin.py` or create a new file
2. Inherit from `Tool` base class
3. Implement the `execute` method
4. Add the tool to `get_builtin_tools()` function

Example:

```python
from app.tools.base import Tool
from typing import Any


class MyNewTool(Tool):
    name: str = "my_new_tool"
    description: str = "Description of what this tool does"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }

    async def execute(self, param1: str) -> str:
        # Your implementation here
        result = f"Processed: {param1}"
        return result
```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test both success and failure cases
- Use pytest fixtures for common setup

### Example Test

```python
import pytest
from app.tools.builtin import MyNewTool


@pytest.mark.asyncio
async def test_my_new_tool_success():
    """Test successful execution of MyNewTool"""
    tool = MyNewTool()
    result = await tool.execute(param1="test")
    assert "test" in result


@pytest.mark.asyncio
async def test_my_new_tool_error():
    """Test error handling in MyNewTool"""
    tool = MyNewTool()
    with pytest.raises(ValueError):
        await tool.execute(param1="")
```

## Documentation

- Update README.md if you add new features
- Add docstrings to all public APIs
- Update AWS_DEPLOYMENT.md for deployment-related changes
- Add examples in the `examples/` directory

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## Questions?

If you have questions:
- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
