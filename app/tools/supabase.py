"""
Supabase integration tools for database and auth setup
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

import requests
from loguru import logger

from app.config import get_config
from app.tools.base import Tool


class SupabaseProjectTool(Tool):
    """
    Create or connect to Supabase project
    """

    name: str = "supabase_project"
    description: str = "Create a new Supabase project or connect to existing one. Returns project credentials."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "description": "Name for the Supabase project",
            },
            "organization_id": {
                "type": "string",
                "description": "Supabase organization ID (optional, will use default)",
            },
            "db_password": {
                "type": "string",
                "description": "Database password (will generate if not provided)",
            },
            "region": {
                "type": "string",
                "description": "Region for the project (e.g., 'us-east-1')",
                "default": "us-east-1",
            },
        },
        "required": ["project_name"],
    }

    async def execute(
        self,
        project_name: str,
        organization_id: Optional[str] = None,
        db_password: Optional[str] = None,
        region: str = "us-east-1",
    ) -> str:
        """
        Create Supabase project

        Args:
            project_name: Project name
            organization_id: Organization ID
            db_password: Database password
            region: AWS region

        Returns:
            Project credentials and info
        """
        try:
            # Check for Supabase access token
            access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
            if not access_token:
                return """Error: SUPABASE_ACCESS_TOKEN not set.

Get your access token from: https://app.supabase.com/account/tokens

Then set it:
export SUPABASE_ACCESS_TOKEN="your-token-here"
"""

            # For automation, we'll guide the user through manual setup
            # In production, you'd use Supabase Management API

            setup_guide = f"""
## Supabase Project Setup

### Option 1: Manual Setup (Recommended for now)
1. Go to https://app.supabase.com
2. Create new project: {project_name}
3. Region: {region}
4. Set database password (save it!)
5. Wait for project to provision (~2 minutes)

### Option 2: Get Credentials from Existing Project
1. Go to project settings
2. Navigate to API section
3. Copy these values:

### Required Credentials:
Save these to your .env file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Next Steps:
After getting credentials, run:
- supabase_create_schema to set up database tables
- supabase_enable_auth to configure authentication

Project Name: {project_name}
Region: {region}
"""

            # Save project info
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            project_file = workspace / "supabase_project.json"

            project_info = {
                "name": project_name,
                "region": region,
                "status": "pending_manual_setup",
            }

            with open(project_file, "w") as f:
                json.dump(project_info, f, indent=2)

            return setup_guide

        except Exception as e:
            logger.error(f"Supabase project error: {str(e)}")
            return f"Error: {str(e)}"


class SupabaseCreateSchemaTool(Tool):
    """
    Create database schema with migrations
    """

    name: str = "supabase_create_schema"
    description: str = "Create SaaS database schema with profiles, subscriptions, products, and entitlements tables. Includes RLS policies."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "include_products": {
                "type": "boolean",
                "description": "Include products/prices tables for Stripe sync",
                "default": True,
            },
            "include_payments": {
                "type": "boolean",
                "description": "Include payments table for transaction history",
                "default": True,
            },
        },
        "required": [],
    }

    async def execute(
        self, include_products: bool = True, include_payments: bool = True
    ) -> str:
        """
        Create database schema

        Args:
            include_products: Include products tables
            include_payments: Include payments table

        Returns:
            SQL migration file path
        """
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            migrations_dir = workspace / "supabase" / "migrations"
            migrations_dir.mkdir(parents=True, exist_ok=True)

            # Generate timestamp for migration
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            migration_file = migrations_dir / f"{timestamp}_initial_schema.sql"

            # Build SQL schema
            sql_parts = []

            # Profiles table
            sql_parts.append(
                """
-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profiles RLS policies
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
"""
            )

            # Subscriptions table
            sql_parts.append(
                """
-- Subscriptions table (mirrors Stripe)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id TEXT PRIMARY KEY, -- Stripe subscription ID
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    status TEXT NOT NULL, -- active, canceled, past_due, etc.
    plan_id TEXT, -- Stripe price ID
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on subscriptions
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Subscriptions RLS policies
CREATE POLICY "Users can view own subscriptions"
    ON public.subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Index for lookups
CREATE INDEX IF NOT EXISTS subscriptions_user_id_idx ON public.subscriptions(user_id);
"""
            )

            # Products table (optional)
            if include_products:
                sql_parts.append(
                    """
-- Products table (Stripe product cache)
CREATE TABLE IF NOT EXISTS public.products (
    id TEXT PRIMARY KEY, -- Stripe product ID
    name TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prices table (Stripe prices)
CREATE TABLE IF NOT EXISTS public.prices (
    id TEXT PRIMARY KEY, -- Stripe price ID
    product_id TEXT REFERENCES public.products(id),
    active BOOLEAN DEFAULT TRUE,
    currency TEXT DEFAULT 'usd',
    unit_amount INTEGER, -- in cents
    interval TEXT, -- month, year
    interval_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Public read access for products/prices
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Products are viewable by everyone"
    ON public.products FOR SELECT
    USING (active = TRUE);

CREATE POLICY "Prices are viewable by everyone"
    ON public.prices FOR SELECT
    USING (active = TRUE);
"""
                )

            # Payments table (optional)
            if include_payments:
                sql_parts.append(
                    """
-- Payments table (transaction history)
CREATE TABLE IF NOT EXISTS public.payments (
    id TEXT PRIMARY KEY, -- Stripe payment intent ID
    user_id UUID REFERENCES auth.users(id),
    subscription_id TEXT REFERENCES public.subscriptions(id),
    amount INTEGER NOT NULL, -- in cents
    currency TEXT DEFAULT 'usd',
    status TEXT NOT NULL, -- succeeded, failed, pending
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on payments
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Payments RLS policies
CREATE POLICY "Users can view own payments"
    ON public.payments FOR SELECT
    USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS payments_user_id_idx ON public.payments(user_id);
"""
                )

            # Entitlements table
            sql_parts.append(
                """
-- Entitlements table (feature flags / plan gates)
CREATE TABLE IF NOT EXISTS public.entitlements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    feature_key TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    quota INTEGER, -- optional usage limit
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature_key)
);

-- Enable RLS on entitlements
ALTER TABLE public.entitlements ENABLE ROW LEVEL SECURITY;

-- Entitlements RLS policies
CREATE POLICY "Users can view own entitlements"
    ON public.entitlements FOR SELECT
    USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS entitlements_user_id_idx ON public.entitlements(user_id);
"""
            )

            # Combine all SQL
            full_sql = "\n".join(sql_parts)

            # Write migration file
            with open(migration_file, "w") as f:
                f.write(full_sql)

            result = f"""
✅ Database schema created!

Migration file: {migration_file}

Tables created:
- profiles (user metadata + RLS)
- subscriptions (Stripe sync + RLS)
{"- products (Stripe product cache)" if include_products else ""}
{"- prices (Stripe pricing)" if include_products else ""}
{"- payments (transaction history)" if include_payments else ""}
- entitlements (feature flags)

Next steps:
1. Run this migration on your Supabase project:
   - Copy the SQL from {migration_file}
   - Go to Supabase SQL Editor
   - Paste and execute

2. Or use Supabase CLI:
   supabase db push

All tables have Row Level Security (RLS) enabled!
"""

            return result

        except Exception as e:
            logger.error(f"Schema creation error: {str(e)}")
            return f"Error: {str(e)}"


class SupabaseEnableAuthTool(Tool):
    """
    Configure Supabase Auth settings
    """

    name: str = "supabase_enable_auth"
    description: str = "Configure Supabase authentication with email, magic link, and OAuth providers."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "enable_email": {
                "type": "boolean",
                "description": "Enable email/password auth",
                "default": True,
            },
            "enable_magic_link": {
                "type": "boolean",
                "description": "Enable magic link (passwordless) auth",
                "default": True,
            },
            "enable_google": {
                "type": "boolean",
                "description": "Enable Google OAuth",
                "default": False,
            },
        },
        "required": [],
    }

    async def execute(
        self,
        enable_email: bool = True,
        enable_magic_link: bool = True,
        enable_google: bool = False,
    ) -> str:
        """
        Configure auth settings

        Args:
            enable_email: Enable email auth
            enable_magic_link: Enable magic link
            enable_google: Enable Google OAuth

        Returns:
            Configuration guide
        """
        try:
            config_guide = """
## Supabase Auth Configuration

### 1. Email/Password Auth
"""
            if enable_email:
                config_guide += """
✅ Enabled by default in Supabase

Configure in dashboard:
1. Go to Authentication > Providers
2. Email provider should be enabled
3. Set confirmation email template (optional)
"""
            else:
                config_guide += "⏭️ Skipped\n"

            config_guide += "\n### 2. Magic Link Auth\n"
            if enable_magic_link:
                config_guide += """
✅ Enable in dashboard:
1. Go to Authentication > Providers
2. Enable "Email (Magic Link)"
3. Configure email templates
"""
            else:
                config_guide += "⏭️ Skipped\n"

            config_guide += "\n### 3. Google OAuth\n"
            if enable_google:
                config_guide += """
✅ Setup required:
1. Create OAuth app in Google Cloud Console
2. Get Client ID and Client Secret
3. In Supabase:
   - Go to Authentication > Providers
   - Enable Google
   - Enter Client ID and Secret
   - Add callback URL: https://your-project.supabase.co/auth/v1/callback
"""
            else:
                config_guide += "⏭️ Skipped\n"

            config_guide += """
### Client Code Example

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Email/password signup
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123',
})

// Magic link
const { error } = await supabase.auth.signInWithOtp({
  email: 'user@example.com',
})

// Google OAuth
const { error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
})
```

### Security Notes:
- NEVER expose SUPABASE_SERVICE_ROLE_KEY to client
- Use RLS policies to protect data
- Enable email confirmation for production
"""

            return config_guide

        except Exception as e:
            logger.error(f"Auth config error: {str(e)}")
            return f"Error: {str(e)}"
