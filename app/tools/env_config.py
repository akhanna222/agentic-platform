"""
Interactive Environment Variable Configuration Tools
Allows agent to request env variables from user and save them
"""

import os
from pathlib import Path
from typing import Any
from app.tools.base import Tool


class RequestEnvVariableTool(Tool):
    """Request an environment variable from user interactively"""

    name: str = "request_env_variable"
    description: str = "Ask user for an environment variable value and save it to .env file"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "variable_name": {
                "type": "string",
                "description": "Name of the environment variable (e.g., SUPABASE_URL, STRIPE_SECRET_KEY)"
            },
            "description": {
                "type": "string",
                "description": "User-friendly description of what this variable is for"
            },
            "example": {
                "type": "string",
                "description": "Example value format (e.g., 'https://xxxxx.supabase.co' or 'sk_test_...')"
            },
            "required": {
                "type": "boolean",
                "description": "Whether this variable is required to continue",
                "default": True
            },
            "get_from_url": {
                "type": "string",
                "description": "Optional URL where user can find/create this value"
            }
        },
        "required": ["variable_name", "description"]
    }

    async def execute(
        self,
        variable_name: str,
        description: str,
        example: str = None,
        required: bool = True,
        get_from_url: str = None,
        **kwargs
    ) -> str:
        """Request env variable from user"""

        # Check if already set
        existing_value = os.getenv(variable_name)
        env_file = Path('.env')

        if existing_value:
            return f"""
✅ {variable_name} is already configured!

Current value: {existing_value[:20]}...

If you want to update it, please provide the new value.
If you want to keep it, just say "keep it" or "continue".
"""

        # Build the request message
        request_msg = f"""
🔑 I need your **{variable_name}**

**What it's for**: {description}

"""

        if example:
            request_msg += f"**Example format**: `{example}`\n\n"

        if get_from_url:
            request_msg += f"**Get it here**: {get_from_url}\n\n"

        request_msg += f"**Required**: {'Yes - I need this to continue' if required else 'Optional - you can skip this'}\n\n"

        request_msg += "Please enter the value, or say 'skip' if optional."

        return request_msg


class SaveEnvVariableTool(Tool):
    """Save an environment variable to .env file"""

    name: str = "save_env_variable"
    description: str = "Save a user-provided environment variable to .env file"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "variable_name": {
                "type": "string",
                "description": "Name of the environment variable"
            },
            "value": {
                "type": "string",
                "description": "Value provided by the user"
            },
            "validate_format": {
                "type": "boolean",
                "description": "Whether to validate the format",
                "default": True
            }
        },
        "required": ["variable_name", "value"]
    }

    async def execute(
        self,
        variable_name: str,
        value: str,
        validate_format: bool = True,
        **kwargs
    ) -> str:
        """Save env variable"""

        # Basic validation
        if validate_format:
            # Validate Supabase URL
            if "SUPABASE_URL" in variable_name:
                if not value.startswith("https://") or "supabase.co" not in value:
                    return f"⚠️ Warning: {variable_name} doesn't look like a Supabase URL\n" \
                           f"Expected format: https://xxxxx.supabase.co\n" \
                           f"You provided: {value}\n\n" \
                           f"Do you want to use this anyway? (yes/no)"

            # Validate Stripe key
            if "STRIPE" in variable_name and "KEY" in variable_name:
                if not (value.startswith("sk_test_") or value.startswith("sk_live_") or value.startswith("pk_")):
                    return f"⚠️ Warning: {variable_name} doesn't look like a Stripe key\n" \
                           f"Expected to start with: sk_test_, sk_live_, or pk_\n" \
                           f"You provided: {value[:20]}...\n\n" \
                           f"Do you want to use this anyway? (yes/no)"

            # Validate OpenAI key
            if "OPENAI" in variable_name and "KEY" in variable_name:
                if not value.startswith("sk-"):
                    return f"⚠️ Warning: {variable_name} doesn't look like an OpenAI key\n" \
                           f"Expected to start with: sk-\n" \
                           f"You provided: {value[:10]}...\n\n" \
                           f"Do you want to use this anyway? (yes/no)"

        # Save to .env file
        env_file = Path('.env')

        # Read existing .env if it exists
        existing_lines = []
        variable_exists = False

        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{variable_name}="):
                        # Update existing variable
                        existing_lines.append(f"{variable_name}={value}\n")
                        variable_exists = True
                    else:
                        existing_lines.append(line + '\n' if line else '\n')

        # Add new variable if it doesn't exist
        if not variable_exists:
            if not existing_lines or existing_lines[-1].strip():
                existing_lines.append('\n')
            existing_lines.append(f"# {variable_name}\n")
            existing_lines.append(f"{variable_name}={value}\n")

        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(existing_lines)

        # Set in current environment
        os.environ[variable_name] = value

        # Mask sensitive values in response
        masked_value = value[:10] + "..." if len(value) > 10 else value

        return f"""
✅ Saved {variable_name}!

Value: {masked_value}
File: .env

This variable is now available for your app to use.

Ready to continue!
"""


class ListEnvVariablesTool(Tool):
    """List currently configured environment variables"""

    name: str = "list_env_variables"
    description: str = "Show which environment variables are currently configured"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        """List env variables"""

        env_file = Path('.env')

        if not env_file.exists():
            return """
📋 No .env file found yet.

I'll create one as we configure your environment variables.
"""

        # Read .env file
        configured_vars = []

        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var_name, var_value = line.split('=', 1)

                    # Mask sensitive values
                    if 'KEY' in var_name or 'SECRET' in var_name or 'PASSWORD' in var_name:
                        masked = var_value[:10] + "..." if len(var_value) > 10 else "***"
                    else:
                        masked = var_value[:30] + "..." if len(var_value) > 30 else var_value

                    configured_vars.append(f"✅ {var_name}: {masked}")

        if not configured_vars:
            return """
📋 .env file exists but is empty.

No variables configured yet.
"""

        result = "📋 Currently Configured Variables:\n\n"
        result += "\n".join(configured_vars)
        result += "\n\nThese are saved in your .env file and ready to use!"

        return result


class ClearEnvVariableTool(Tool):
    """Remove an environment variable"""

    name: str = "clear_env_variable"
    description: str = "Remove an environment variable from .env file"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "variable_name": {
                "type": "string",
                "description": "Name of the variable to remove"
            }
        },
        "required": ["variable_name"]
    }

    async def execute(self, variable_name: str, **kwargs) -> str:
        """Clear env variable"""

        env_file = Path('.env')

        if not env_file.exists():
            return f"ℹ️ No .env file found. {variable_name} doesn't exist."

        # Read and filter out the variable
        lines = []
        found = False

        with open(env_file, 'r') as f:
            skip_next_comment = False
            for line in f:
                if line.strip().startswith(f"# {variable_name}"):
                    skip_next_comment = True
                    continue
                elif line.strip().startswith(f"{variable_name}="):
                    found = True
                    continue
                elif skip_next_comment and line.strip().startswith('#'):
                    skip_next_comment = False
                    continue
                lines.append(line)

        if not found:
            return f"ℹ️ {variable_name} was not found in .env file."

        # Write back
        with open(env_file, 'w') as f:
            f.writelines(lines)

        # Remove from current environment
        if variable_name in os.environ:
            del os.environ[variable_name]

        return f"✅ Removed {variable_name} from .env file."
