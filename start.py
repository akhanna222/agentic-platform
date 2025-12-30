#!/usr/bin/env python3
"""
Agentic Platform - Interactive Setup & Launch Script
User-friendly script to configure and start the platform
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🤖  AGENTIC PLATFORM - Interactive Setup  🤖       ║
║                                                           ║
║     Build SaaS apps • Automate tasks • Beautiful UI      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check if Python version is compatible"""
    print_section("Checking Python Version")

    version = sys.version_info
    if version < (3, 11) or version >= (3, 14):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  Recommended: Python 3.11, 3.12, or 3.13")

        response = input("\nContinue anyway? (y/n): ").lower()
        if response != 'y':
            print("\n👋 Exiting. Please install Python 3.11+ and try again.")
            sys.exit(0)
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Perfect!")


def setup_virtual_environment():
    """Set up virtual environment if needed"""
    venv_path = Path("venv")

    if venv_path.exists():
        print("✅ Virtual environment found")
        return True

    print("📦 Creating virtual environment...")
    print("   This avoids system package conflicts")

    try:
        subprocess.run(
            [sys.executable, "-m", "venv", "venv"],
            check=True
        )
        print("✅ Virtual environment created!")
        print("\n💡 To use it manually:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate    # Windows")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Could not create virtual environment")
        return False


def get_python_executable():
    """Get the appropriate Python executable (venv or system)"""
    venv_path = Path("venv")

    if venv_path.exists():
        # Use venv python
        if os.name == 'nt':  # Windows
            return str(venv_path / "Scripts" / "python")
        else:  # Linux/Mac
            return str(venv_path / "bin" / "python")
    else:
        # Use system python
        return sys.executable


def get_pip_command():
    """Get the appropriate pip command (venv or system)"""
    venv_path = Path("venv")

    if venv_path.exists():
        # Use venv pip
        if os.name == 'nt':  # Windows
            return str(venv_path / "Scripts" / "pip")
        else:  # Linux/Mac
            return str(venv_path / "bin" / "pip")
    else:
        # Use system pip
        return sys.executable + " -m pip"


def check_dependencies():
    """Check if dependencies are installed"""
    print_section("Checking Dependencies")

    required = ['pydantic', 'openai', 'fastapi', 'uvicorn']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing {len(missing)} package(s)")

        # Check for externally-managed-environment error
        is_ubuntu = os.path.exists('/etc/lsb-release')

        if is_ubuntu and not Path("venv").exists():
            print("\n🔧 Detected Ubuntu/Debian - Setting up virtual environment...")
            setup_virtual_environment()

        print("\nInstalling minimal dependencies...")

        try:
            pip_cmd = get_pip_command()

            if isinstance(pip_cmd, str) and ' ' in pip_cmd:
                # It's a command like "python -m pip"
                cmd_parts = pip_cmd.split() + ["install", "-q", "-r", "requirements-minimal.txt"]
            else:
                # It's a path to pip
                cmd_parts = [pip_cmd, "install", "-q", "-r", "requirements-minimal.txt"]

            subprocess.run(cmd_parts, check=True)
            print("✅ Dependencies installed successfully!")

            # If we used venv, remind user to activate it
            if Path("venv").exists():
                print("\n💡 Virtual environment is set up!")
                print("   For future manual use, activate it first:")
                print("   source venv/bin/activate  # Linux/Mac")

        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print("\n🔧 Manual fix options:")
            print("\n   Option 1: Use virtual environment (recommended)")
            print("   python3 -m venv venv")
            print("   source venv/bin/activate")
            print("   pip install -r requirements-minimal.txt")
            print("\n   Option 2: Use --break-system-packages (not recommended)")
            print("   pip install -r requirements-minimal.txt --break-system-packages")
            sys.exit(1)
    else:
        print("\n✅ All dependencies installed!")


def get_env_value(key, description, required=True, default=None, secret=False):
    """Get environment variable value from user"""
    # Check if already set
    existing = os.getenv(key)
    if existing:
        if secret:
            masked = existing[:10] + "..." if len(existing) > 10 else existing
            print(f"✅ {key} already set: {masked}")
        else:
            print(f"✅ {key} already set: {existing}")

        response = input(f"   Keep this value? (y/n): ").lower()
        if response == 'y':
            return existing

    # Get new value
    if required:
        prompt = f"{description} (required): "
    else:
        prompt = f"{description} (optional, press Enter to skip): "

    while True:
        value = input(prompt).strip()

        if not value:
            if required:
                print("❌ This field is required!")
                continue
            else:
                return default or ""

        # Validate OpenAI key format
        if key == "OPENAI_API_KEY":
            if not (value.startswith("sk-") and len(value) > 20):
                print("⚠️  Warning: Doesn't look like a valid OpenAI key (should start with 'sk-')")
                response = input("   Continue anyway? (y/n): ").lower()
                if response != 'y':
                    continue

        return value


def configure_environment():
    """Interactive environment configuration"""
    print_section("Environment Configuration")

    print("Let's set up your API keys and configuration.\n")

    env_vars = {}

    # Required: OpenAI API Key
    print("🔑 OpenAI API Key")
    print("   Get one at: https://platform.openai.com/api-keys\n")
    env_vars['OPENAI_API_KEY'] = get_env_value(
        'OPENAI_API_KEY',
        'Enter your OpenAI API key',
        required=True,
        secret=True
    )

    # Optional: Model selection
    print("\n🤖 LLM Model")
    print("   Recommended: gpt-4o-mini (faster, cheaper)")
    print("   Advanced: gpt-4o (more capable, expensive)\n")
    model = input("Model name (press Enter for gpt-4o-mini): ").strip()
    env_vars['OPENAI_MODEL'] = model or 'gpt-4o-mini'

    # Optional: Advanced configurations
    print("\n⚙️  Advanced Configuration (Optional)")
    response = input("Configure Supabase, Stripe, etc.? (y/n): ").lower()

    if response == 'y':
        print("\n📦 Supabase (for SaaS apps)")
        supabase_url = input("Supabase URL (optional): ").strip()
        if supabase_url:
            env_vars['SUPABASE_URL'] = supabase_url
            env_vars['SUPABASE_KEY'] = input("Supabase anon key: ").strip()

        print("\n💳 Stripe (for payments)")
        stripe_key = input("Stripe secret key (optional): ").strip()
        if stripe_key:
            env_vars['STRIPE_SECRET_KEY'] = stripe_key

    # Save to .env file
    env_file = Path('.env')
    print(f"\n💾 Saving configuration to {env_file}...")

    with open(env_file, 'w') as f:
        f.write("# Agentic Platform Configuration\n")
        f.write(f"# Generated by start.py\n\n")

        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
            # Set in current environment
            os.environ[key] = value

    print(f"✅ Configuration saved to {env_file}")

    return env_vars


def test_connection():
    """Test OpenAI connection"""
    print_section("Testing Connection")

    print("Testing OpenAI API connection...")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Simple test call
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )

        result = response.choices[0].message.content.lower()

        if 'test successful' in result or 'success' in result:
            print("✅ OpenAI API connection successful!")
            return True
        else:
            print("⚠️  API responded but with unexpected output")
            print(f"   Response: {result}")
            return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Common fixes:")
        print("   1. Check your API key is correct")
        print("   2. Verify you have API credits")
        print("   3. Check your internet connection")
        return False


def show_menu():
    """Show main menu"""
    print_section("What would you like to do?")

    print("1. 🌐 Start Web UI (recommended)")
    print("2. 💻 Run CLI Agent")
    print("3. 🧪 Test All Components")
    print("4. 📚 View Documentation")
    print("5. ⚙️  Reconfigure Settings")
    print("6. 🚪 Exit")

    choice = input("\nEnter your choice (1-6): ").strip()
    return choice


def start_web_ui():
    """Start the web UI server"""
    print_section("Starting Web UI")

    print("🚀 Launching web server...")
    print("   URL: http://localhost:8005")
    print("   Press Ctrl+C to stop\n")

    try:
        python_exe = get_python_executable()
        subprocess.run([python_exe, "web_server.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Web server stopped")


def run_cli_agent():
    """Run CLI agent"""
    print_section("CLI Agent")

    print("Available agents:")
    print("  platform - General-purpose (default)")
    print("  browser  - Web automation")
    print("  data     - Data analysis")
    print("  ship     - SaaS builder")
    print("  test     - System validator")

    agent = input("\nAgent type (press Enter for platform): ").strip() or "platform"
    prompt = input("Task description: ").strip()

    if not prompt:
        print("❌ Task description required")
        return

    python_exe = get_python_executable()
    cmd = [python_exe, "main.py", "--agent", agent, "--prompt", prompt]

    print(f"\n🤖 Running {agent} agent...")
    subprocess.run(cmd)


def test_components():
    """Run component tests"""
    print_section("Testing Components")

    print("🧪 Running health check...\n")

    python_exe = get_python_executable()
    cmd = [python_exe, "main.py", "--agent", "test", "--prompt", "Run comprehensive health check"]
    subprocess.run(cmd)


def view_documentation():
    """Show documentation links"""
    print_section("Documentation")

    print("📚 Available Documentation:\n")
    print("Quick Start:")
    print("  • QUICKSTART.md - Get started in 5 minutes")
    print("  • README.md - Main documentation\n")

    print("Guides:")
    print("  • docs/guides/INSTALLATION.md - Installation options")
    print("  • docs/guides/FULLSTACK_SHIP_GUIDE.md - Build SaaS apps")
    print("  • docs/guides/CONTRIBUTING.md - Contributing\n")

    print("Deployment:")
    print("  • docs/deployment/AWS_QUICK_START.md - AWS in 10 minutes")
    print("  • docs/deployment/WEB_UI_DEPLOYMENT.md - Web UI deployment\n")

    input("Press Enter to continue...")


def main():
    """Main interactive setup"""
    try:
        print_banner()

        # Check system
        check_python_version()
        check_dependencies()

        # Configure if needed
        env_file = Path('.env')
        if not env_file.exists() or not os.getenv('OPENAI_API_KEY'):
            configure_environment()
        else:
            print_section("Configuration")
            print(f"✅ Found existing .env file")

            # Load existing .env
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value

            response = input("Reconfigure? (y/n): ").lower()
            if response == 'y':
                configure_environment()

        # Test connection
        if not test_connection():
            print("\n⚠️  Warning: Connection test failed")
            response = input("Continue anyway? (y/n): ").lower()
            if response != 'y':
                sys.exit(1)

        # Main loop
        while True:
            choice = show_menu()

            if choice == '1':
                start_web_ui()
            elif choice == '2':
                run_cli_agent()
            elif choice == '3':
                test_components()
            elif choice == '4':
                view_documentation()
            elif choice == '5':
                configure_environment()
                test_connection()
            elif choice == '6':
                print("\n👋 Thanks for using Agentic Platform!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")

    except KeyboardInterrupt:
        print("\n\n👋 Exiting. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 For help, see QUICKSTART.md or open an issue on GitHub")
        sys.exit(1)


if __name__ == "__main__":
    main()
