"""
Deployment tools for Replit, Vercel, and other platforms
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from app.config import get_config
from app.tools.base import Tool


class ReplitDeployTool(Tool):
    """
    Deploy to Replit
    """

    name: str = "replit_deploy"
    description: str = "Deploy app to Replit and get a public URL."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "Name for the Replit project",
            },
            "framework": {
                "type": "string",
                "description": "Framework being deployed",
                "enum": ["nextjs", "react", "nodejs"],
                "default": "nextjs",
            },
        },
        "required": ["project_name"],
    }

    async def execute(self, project_name: str, framework: str = "nextjs") -> str:
        """
        Deploy to Replit

        Args:
            project_name: Project name
            framework: Framework type

        Returns:
            Deployment guide
        """
        try:
            guide = f'''
## Replit Deployment Guide

### Option 1: Import from GitHub (Recommended)

1. Go to https://replit.com
2. Click "Create Repl"
3. Select "Import from GitHub"
4. Enter your repository URL
5. Replit will auto-detect the framework

### Option 2: Manual Setup

1. Create new Repl with Node.js template
2. Upload your code or import from GitHub
3. Set environment variables

### Configure Environment Variables

Go to Secrets (🔒 icon in left sidebar) and add:

**Supabase:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Stripe:**
```
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
```

**App:**
```
APP_URL=https://your-repl.replit.app
```

### Deploy

1. Click "Deploy" button
2. Configure deployment settings
3. Click "Deploy"
4. Your app will be live at: `https://{project_name.lower().replace(" ", "-")}-username.replit.app`

### Custom Domain (Optional)

1. Go to deployment settings
2. Click "Custom domains"
3. Add your domain
4. Update DNS records as instructed

### Replit .replit Config

Create `.replit` file in your project:

```toml
run = "npm run dev"
entrypoint = "package.json"

[deployment]
run = ["npm", "run", "start"]
deploymentTarget = "cloudrun"
build = ["npm", "run", "build"]

[env]
NODE_ENV = "production"
```

### Next Steps

1. Push your code to GitHub
2. Import to Replit
3. Set environment variables
4. Deploy!

Your app will be live and publicly accessible.
'''

            # Save deployment config
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            deploy_file = workspace / "replit_deployment.md"

            with open(deploy_file, "w") as f:
                f.write(guide)

            return guide + f"\n\n💾 Saved to: {deploy_file}"

        except Exception as e:
            logger.error(f"Replit deploy error: {str(e)}")
            return f"Error: {str(e)}"


class VercelDeployTool(Tool):
    """
    Deploy to Vercel
    """

    name: str = "vercel_deploy"
    description: str = "Deploy Next.js app to Vercel with automatic setup."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "Name for the Vercel project",
            },
            "github_repo": {
                "type": "string",
                "description": "GitHub repository URL (optional)",
            },
        },
        "required": ["project_name"],
    }

    async def execute(self, project_name: str, github_repo: Optional[str] = None) -> str:
        """
        Deploy to Vercel

        Args:
            project_name: Project name
            github_repo: GitHub repo URL

        Returns:
            Deployment guide
        """
        try:
            guide = f'''
## Vercel Deployment Guide

Vercel is the easiest way to deploy Next.js apps!

### Quick Deploy

**Option 1: Deploy from GitHub (Best)**

1. Push your code to GitHub
2. Go to https://vercel.com
3. Click "New Project"
4. Import your GitHub repository
5. Vercel auto-detects Next.js
6. Click "Deploy"

**Option 2: Deploy with Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel
```

### Environment Variables

In Vercel dashboard, go to Settings > Environment Variables and add:

**Supabase:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Stripe:**
```
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
```

**App:**
```
APP_URL=https://your-project.vercel.app
```

### Important: Update Stripe Webhook URL

After deployment, update your Stripe webhook endpoint:
1. Copy your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Go to Stripe Dashboard > Webhooks
3. Update endpoint to: `https://your-project.vercel.app/api/webhooks/stripe`

### Custom Domain

1. Go to Project Settings > Domains
2. Add your domain
3. Update DNS records

Vercel provides automatic HTTPS for all domains!

### Automatic Deployments

Vercel automatically deploys when you push to your GitHub main branch.

- Push to `main` → Production deployment
- Push to other branches → Preview deployments

### vercel.json Configuration

Create `vercel.json` in project root:

```json
{{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {{
    "APP_URL": "https://{project_name.lower().replace(" ", "-")}.vercel.app"
  }}
}}
```

### Your Deployment URL

After deployment, your app will be available at:
`https://{project_name.lower().replace(" ", "-")}.vercel.app`

### Monitoring

Vercel provides:
- Real-time logs
- Analytics
- Performance monitoring
- Error tracking

Access from your project dashboard.
'''

            # Save deployment config
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            deploy_file = workspace / "vercel_deployment.md"

            with open(deploy_file, "w") as f:
                f.write(guide)

            return guide + f"\n\n💾 Saved to: {deploy_file}"

        except Exception as e:
            logger.error(f"Vercel deploy error: {str(e)}")
            return f"Error: {str(e)}"


class GenerateEnvFileTool(Tool):
    """
    Generate .env template file
    """

    name: str = "generate_env_file"
    description: str = "Generate .env.example and .env.local template files with all required environment variables."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "include_comments": {
                "type": "boolean",
                "description": "Include helpful comments in env file",
                "default": True,
            }
        },
        "required": [],
    }

    async def execute(self, include_comments: bool = True) -> str:
        """
        Generate env files

        Args:
            include_comments: Include comments

        Returns:
            Generated file paths
        """
        try:
            env_content = ""

            if include_comments:
                env_content += """# ============================================
# Agentic Platform - Environment Variables
# ============================================
# Copy this file to .env.local and fill in your values
# NEVER commit .env.local to git!

"""

            env_content += """# Supabase Configuration
# Get these from: https://app.supabase.com/project/_/settings/api
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Stripe Configuration
# Get these from: https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Stripe Webhooks
# Get this from: https://dashboard.stripe.com/webhooks
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Stripe Price IDs
# Get these from: https://dashboard.stripe.com/products
STRIPE_PRICE_BASIC=price_your_basic_price_id
STRIPE_PRICE_PRO=price_your_pro_price_id

# Application URL
# Use your deployment URL (Vercel, Replit, etc.)
APP_URL=http://localhost:3000

# Optional: OpenAI (if using AI features)
# OPENAI_API_KEY=sk-your-openai-key-here
"""

            # Save both .env.example and .env.local template
            config = get_config()
            workspace = Path(config.platform.workspace_dir)

            example_file = workspace / ".env.example"
            local_file = workspace / ".env.local.template"

            with open(example_file, "w") as f:
                f.write(env_content)

            with open(local_file, "w") as f:
                f.write(env_content)

            result = f"""
✅ Environment files created!

Files:
- {example_file} (commit this to git)
- {local_file} (copy to .env.local and fill in)

Next steps:
1. Copy .env.local.template to .env.local
2. Fill in your actual credentials
3. Never commit .env.local to git!

Add to .gitignore:
```
.env.local
.env
```

Quick setup checklist:
□ Supabase project created
□ Stripe products/prices created
□ Webhook endpoint configured
□ Environment variables set in deployment platform
"""

            return result

        except Exception as e:
            logger.error(f"Env file generation error: {str(e)}")
            return f"Error: {str(e)}"
