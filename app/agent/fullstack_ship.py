"""
FullStack Ship Agent - End-to-end SaaS app builder
Implements the Lovable/Replit/Base44 stack and workflow
"""

from loguru import logger

from app.agent.toolcall import ToolCallAgent
from app.tools.collection import ToolCollection
from app.tools.control import TerminateTool, AskHumanTool
from app.tools.supabase import (
    SupabaseProjectTool,
    SupabaseCreateSchemaTool,
    SupabaseEnableAuthTool,
)
from app.tools.stripe_tools import (
    StripeSetupTool,
    StripeCheckoutCodeTool,
    StripeWebhookCodeTool,
)
from app.tools.deployment import (
    ReplitDeployTool,
    VercelDeployTool,
    GenerateEnvFileTool,
)
from app.tools.builtin import FileWriteTool, FileReadTool, FileListTool


FULLSTACK_SHIP_SYSTEM_PROMPT = """You are a FullStack Ship Agent - an expert at building and deploying complete SaaS applications.

Your mission: Build a production-ready SaaS app following the Lovable/Replit/Base44 stack:
- Frontend: Next.js (React)
- Backend: Supabase (Postgres + Auth + Storage)
- Payments: Stripe (Checkout + Webhooks)
- Hosting: Replit or Vercel

## Your Workflow (6 Phases):

### Phase 1: Understand Requirements
- Ask the user about their SaaS idea
- Clarify features, pricing, and goals
- Confirm the stack choices

### Phase 2: Set Up Supabase (Database + Auth)
1. Guide user to create Supabase project
2. Generate database schema with migrations:
   - profiles table (user metadata)
   - subscriptions table (Stripe sync)
   - products/prices tables (optional)
   - entitlements table (feature flags)
3. Enable Row Level Security (RLS) with policies
4. Configure authentication (email, magic link, OAuth)

### Phase 3: Set Up Stripe (Payments)
1. Guide user to get Stripe keys
2. Help create products and subscription prices
3. Generate Checkout Session endpoint code
4. Generate Webhook handler code for subscription sync
5. Explain webhook setup in Stripe dashboard

### Phase 4: Generate Application Code
1. Create Next.js project structure
2. Generate auth pages (login, signup, protected routes)
3. Generate pricing page with Stripe Checkout
4. Generate dashboard with subscription status
5. Add environment variable templates

### Phase 5: Deploy to Platform
1. Generate deployment configuration
2. Guide environment variable setup
3. Provide deployment instructions for:
   - Replit (with .replit config)
   - Vercel (with vercel.json)
4. Return public URL

### Phase 6: Verification & Next Steps
1. Verify deployment is accessible
2. Test auth flow works
3. Test Stripe checkout creates session
4. Provide post-deployment checklist
5. Suggest next features to build

## Key Principles:
- Always use migrations for database changes (deterministic)
- Always enable RLS on tables (security)
- Never expose service-role keys to client
- Use server-only endpoints for Stripe operations
- Verify webhook signatures
- Provide clear, copy-paste ready code
- Guide step-by-step with checkboxes

## Tools Available:
- supabase_project: Set up Supabase project
- supabase_create_schema: Generate database migrations
- supabase_enable_auth: Configure authentication
- stripe_setup: Create Stripe products/prices
- stripe_checkout_code: Generate checkout endpoint
- stripe_webhook_code: Generate webhook handler
- replit_deploy / vercel_deploy: Deployment guides
- generate_env_file: Create .env templates
- file_write: Create code files
- ask_human: Ask user for input/decisions
- terminate: Signal completion

## Communication Style:
- Be enthusiastic and encouraging
- Use emojis for visual clarity (✅ ❌ 🚀 💡)
- Provide checklists for tracking progress
- Explain WHY you're doing each step
- Celebrate milestones!

When ready, say "Ship it! 🚀" and return the live URL.
"""


class FullStackShipAgent(ToolCallAgent):
    """
    Specialized agent for shipping complete SaaS applications

    Implements the full Lovable/Replit/Base44 stack:
    - Next.js frontend
    - Supabase backend
    - Stripe payments
    - Automated deployment
    """

    system_prompt: str = FULLSTACK_SHIP_SYSTEM_PROMPT
    max_steps: int = 50  # More steps needed for full app

    def __init__(self, **data):
        # Initialize with fullstack tools
        if "tool_collection" not in data:
            data["tool_collection"] = ToolCollection()

            # Supabase tools
            data["tool_collection"].add_tool(SupabaseProjectTool())
            data["tool_collection"].add_tool(SupabaseCreateSchemaTool())
            data["tool_collection"].add_tool(SupabaseEnableAuthTool())

            # Stripe tools
            data["tool_collection"].add_tool(StripeSetupTool())
            data["tool_collection"].add_tool(StripeCheckoutCodeTool())
            data["tool_collection"].add_tool(StripeWebhookCodeTool())

            # Deployment tools
            data["tool_collection"].add_tool(ReplitDeployTool())
            data["tool_collection"].add_tool(VercelDeployTool())
            data["tool_collection"].add_tool(GenerateEnvFileTool())

            # File tools
            data["tool_collection"].add_tool(FileWriteTool())
            data["tool_collection"].add_tool(FileReadTool())
            data["tool_collection"].add_tool(FileListTool())

            # Control tools
            data["tool_collection"].add_tool(AskHumanTool())
            data["tool_collection"].add_tool(TerminateTool())

        if "name" not in data:
            data["name"] = "FullStackShipAgent"
        if "description" not in data:
            data["description"] = "End-to-end SaaS application builder and deployment agent"

        super().__init__(**data)

    @classmethod
    async def create(cls, **kwargs) -> "FullStackShipAgent":
        """
        Factory method to create fullstack ship agent

        Returns:
            Initialized FullStackShipAgent
        """
        agent = cls(**kwargs)
        logger.info(
            f"Created FullStackShipAgent with {len(agent.tool_collection.tools)} tools"
        )
        return agent

    def get_phase_checklist(self) -> str:
        """
        Get the 6-phase checklist for tracking progress

        Returns:
            Formatted checklist
        """
        return """
## 🚀 SaaS Ship Checklist

### Phase 1: Requirements ✓
□ SaaS idea clarified
□ Features defined
□ Pricing model confirmed

### Phase 2: Supabase Setup
□ Project created
□ Database schema generated
□ RLS policies enabled
□ Auth configured

### Phase 3: Stripe Setup
□ API keys obtained
□ Products created
□ Prices configured
□ Checkout code generated
□ Webhook handler generated

### Phase 4: Application Code
□ Next.js structure created
□ Auth pages generated
□ Pricing page created
□ Dashboard built
□ .env template created

### Phase 5: Deployment
□ Platform selected
□ Environment variables set
□ Code deployed
□ Public URL obtained

### Phase 6: Verification
□ Deployment accessible
□ Auth flow tested
□ Checkout flow tested
□ Webhook endpoint verified
□ Ready for users!

Ship it! 🚀
"""
