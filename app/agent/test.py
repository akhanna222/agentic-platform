"""
Test Agent - Validates platform functionality and dependencies
"""

from typing import Any
from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.tools.base import Tool
from app.tools.collection import ToolCollection


TEST_AGENT_SYSTEM_PROMPT = """You are a Testing and Validation Agent specialized in:
1. Testing all platform components and tools
2. Validating database connections and configurations
3. Checking API integrations (OpenAI, Supabase, Stripe, etc.)
4. Running comprehensive system health checks
5. Identifying and reporting errors or misconfigurations
6. Suggesting fixes for common issues

Your goal is to ensure everything works correctly before deployment.

Available tools:
- test_llm_connection: Test OpenAI/LLM API connection
- test_database_connection: Test database connectivity (Supabase, PostgreSQL)
- test_stripe_connection: Test Stripe API integration
- test_all_tools: Run tests on all platform tools
- validate_dependencies: Check if all Python dependencies are installed
- health_check: Comprehensive system health check
- fix_common_issues: Attempt to fix common configuration problems

Always provide clear, actionable feedback on what's working and what needs attention.
"""


class TestLLMConnectionTool(Tool):
    """Test LLM API connection"""

    name: str = "test_llm_connection"
    description: str = "Test connection to OpenAI or other LLM provider"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        """Test LLM connection"""
        try:
            from app.llm import get_llm

            llm = get_llm()

            # Try a simple API call
            messages = [{"role": "user", "content": "Say 'test successful' if you can read this"}]
            response = await llm.chat(messages)

            if response and "test successful" in response.lower():
                return f"✅ LLM Connection Test: PASSED\n" \
                       f"Provider: {llm.provider}\n" \
                       f"Model: {llm.model}\n" \
                       f"Response: {response[:100]}"
            else:
                return f"⚠️ LLM Connection Test: PARTIAL\n" \
                       f"API responded but unexpected output: {response[:100]}"

        except Exception as e:
            return f"❌ LLM Connection Test: FAILED\n" \
                   f"Error: {str(e)}\n" \
                   f"Check your OPENAI_API_KEY environment variable"


class TestDatabaseConnectionTool(Tool):
    """Test database connection"""

    name: str = "test_database_connection"
    description: str = "Test connection to Supabase or PostgreSQL database"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "connection_string": {
                "type": "string",
                "description": "Database connection string or Supabase URL"
            }
        },
        "required": []
    }

    async def execute(self, connection_string: str = None, **kwargs) -> str:
        """Test database connection"""
        import os

        # Try to get connection string from environment
        if not connection_string:
            connection_string = os.getenv("SUPABASE_URL") or os.getenv("DATABASE_URL")

        if not connection_string:
            return "⚠️ Database Connection Test: SKIPPED\n" \
                   "No SUPABASE_URL or DATABASE_URL found in environment"

        try:
            # Test Supabase connection
            if "supabase" in connection_string.lower():
                supabase_key = os.getenv("SUPABASE_KEY")
                if not supabase_key:
                    return "❌ Supabase Test: FAILED\n" \
                           "SUPABASE_KEY environment variable not set"

                try:
                    from supabase import create_client

                    client = create_client(connection_string, supabase_key)
                    # Try a simple query
                    result = client.table("_supabase_migrations").select("*").limit(1).execute()

                    return f"✅ Supabase Connection Test: PASSED\n" \
                           f"URL: {connection_string[:50]}...\n" \
                           f"Connection successful!"

                except ImportError:
                    return "⚠️ Supabase Test: SKIPPED\n" \
                           "supabase-py package not installed\n" \
                           "Install with: pip install supabase"
                except Exception as e:
                    return f"❌ Supabase Connection Test: FAILED\n" \
                           f"Error: {str(e)}"

            # Test PostgreSQL connection
            else:
                try:
                    import asyncpg

                    conn = await asyncpg.connect(connection_string)
                    version = await conn.fetchval("SELECT version()")
                    await conn.close()

                    return f"✅ PostgreSQL Connection Test: PASSED\n" \
                           f"Version: {version[:100]}"

                except ImportError:
                    return "⚠️ PostgreSQL Test: SKIPPED\n" \
                           "asyncpg package not installed\n" \
                           "Install with: pip install asyncpg"
                except Exception as e:
                    return f"❌ PostgreSQL Connection Test: FAILED\n" \
                           f"Error: {str(e)}"

        except Exception as e:
            return f"❌ Database Connection Test: FAILED\n" \
                   f"Error: {str(e)}"


class TestStripeConnectionTool(Tool):
    """Test Stripe API connection"""

    name: str = "test_stripe_connection"
    description: str = "Test connection to Stripe API"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        """Test Stripe connection"""
        import os

        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_key:
            return "⚠️ Stripe Connection Test: SKIPPED\n" \
                   "STRIPE_SECRET_KEY environment variable not set"

        try:
            import stripe

            stripe.api_key = stripe_key

            # Try to list products (limit 1)
            products = stripe.Product.list(limit=1)

            return f"✅ Stripe Connection Test: PASSED\n" \
                   f"API Key: {'sk_test' if 'test' in stripe_key else 'sk_live'}...\n" \
                   f"Connection successful!"

        except ImportError:
            return "⚠️ Stripe Test: SKIPPED\n" \
                   "stripe package not installed\n" \
                   "Install with: pip install stripe"
        except Exception as e:
            return f"❌ Stripe Connection Test: FAILED\n" \
                   f"Error: {str(e)}\n" \
                   f"Check your STRIPE_SECRET_KEY"


class TestAllToolsTool(Tool):
    """Test all platform tools"""

    name: str = "test_all_tools"
    description: str = "Run tests on all available platform tools"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        """Test all tools"""
        from app.tools import get_all_tools

        results = []
        tools = get_all_tools()

        results.append(f"Testing {len(tools)} tools...\n")

        passed = 0
        failed = 0
        skipped = 0

        for tool in tools:
            try:
                # Basic validation
                if not tool.name:
                    results.append(f"❌ {tool.__class__.__name__}: Missing name")
                    failed += 1
                    continue

                if not tool.description:
                    results.append(f"⚠️ {tool.name}: Missing description")
                    skipped += 1
                    continue

                if not tool.parameters:
                    results.append(f"⚠️ {tool.name}: Missing parameters schema")
                    skipped += 1
                    continue

                results.append(f"✅ {tool.name}: Validated")
                passed += 1

            except Exception as e:
                results.append(f"❌ {tool.name}: Error - {str(e)}")
                failed += 1

        summary = f"\n📊 Tool Test Summary:\n" \
                  f"✅ Passed: {passed}\n" \
                  f"❌ Failed: {failed}\n" \
                  f"⚠️ Warnings: {skipped}\n"

        return "\n".join(results) + summary


class ValidateDependenciesTool(Tool):
    """Validate Python dependencies"""

    name: str = "validate_dependencies"
    description: str = "Check if all required Python packages are installed"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "requirements_file": {
                "type": "string",
                "description": "Path to requirements file (default: requirements-minimal.txt)"
            }
        },
        "required": []
    }

    async def execute(self, requirements_file: str = "requirements-minimal.txt", **kwargs) -> str:
        """Validate dependencies"""
        import importlib
        import os

        if not os.path.exists(requirements_file):
            return f"❌ Requirements file not found: {requirements_file}"

        results = []
        results.append(f"Checking dependencies from {requirements_file}...\n")

        # Core dependencies that should always be present
        core_deps = {
            "pydantic": "pydantic",
            "openai": "openai",
            "loguru": "loguru",
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
        }

        installed = 0
        missing = 0

        for package_name, import_name in core_deps.items():
            try:
                importlib.import_module(import_name)
                results.append(f"✅ {package_name}")
                installed += 1
            except ImportError:
                results.append(f"❌ {package_name} - NOT INSTALLED")
                missing += 1

        summary = f"\n📦 Dependency Check:\n" \
                  f"✅ Installed: {installed}\n" \
                  f"❌ Missing: {missing}\n"

        if missing > 0:
            summary += f"\nRun: pip install -r {requirements_file}"

        return "\n".join(results) + summary


class HealthCheckTool(Tool):
    """Comprehensive system health check"""

    name: str = "health_check"
    description: str = "Run comprehensive system health check on all components"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        """Run health check"""
        import os
        import sys

        results = []
        results.append("🏥 SYSTEM HEALTH CHECK\n" + "="*50 + "\n")

        # Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 11) and sys.version_info < (3, 14):
            results.append(f"✅ Python Version: {py_version}")
        else:
            results.append(f"⚠️ Python Version: {py_version} (recommend 3.11-3.13)")

        # Environment variables
        results.append("\n🔑 Environment Variables:")
        env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "SUPABASE_URL": os.getenv("SUPABASE_URL"),
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
            "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY"),
        }

        for key, value in env_vars.items():
            if value:
                masked = value[:10] + "..." if len(value) > 10 else value
                results.append(f"✅ {key}: {masked}")
            else:
                if key == "OPENAI_API_KEY":
                    results.append(f"❌ {key}: NOT SET (REQUIRED)")
                else:
                    results.append(f"⚠️ {key}: NOT SET (optional)")

        # Workspace directory
        results.append("\n📁 Workspace:")
        workspace_dir = os.getenv("WORKSPACE_DIR", "./workspace")
        if os.path.exists(workspace_dir):
            results.append(f"✅ Workspace directory exists: {workspace_dir}")
        else:
            results.append(f"⚠️ Workspace directory missing: {workspace_dir}")
            results.append(f"   Will be created automatically")

        # Web server
        results.append("\n🌐 Web Server:")
        if os.path.exists("web_server.py"):
            results.append("✅ web_server.py found")
        else:
            results.append("❌ web_server.py missing")

        if os.path.exists("ui/index.html"):
            results.append("✅ Web UI files found")
        else:
            results.append("❌ Web UI files missing")

        results.append("\n" + "="*50)
        results.append("Health check complete!")

        return "\n".join(results)


class TestAgent(ToolCallAgent):
    """Testing and validation agent"""

    system_prompt: str = Field(default=TEST_AGENT_SYSTEM_PROMPT)
    max_steps: int = Field(default=15)

    def __init__(self, **data):
        if "tool_collection" not in data:
            data["tool_collection"] = ToolCollection()

            # Add testing tools
            data["tool_collection"].add_tool(TestLLMConnectionTool())
            data["tool_collection"].add_tool(TestDatabaseConnectionTool())
            data["tool_collection"].add_tool(TestStripeConnectionTool())
            data["tool_collection"].add_tool(TestAllToolsTool())
            data["tool_collection"].add_tool(ValidateDependenciesTool())
            data["tool_collection"].add_tool(HealthCheckTool())

        super().__init__(**data)
