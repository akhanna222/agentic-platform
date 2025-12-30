"""
User-Guided Supabase Setup Tools
These tools provide instructions for users to configure Supabase themselves
"""

from typing import Any
from app.tools.base import Tool


class SupabaseSetupGuideTool(Tool):
    """Step-by-step guide for user to set up Supabase project"""

    name: str = "supabase_setup_guide"
    description: str = "Provide step-by-step instructions for user to create and configure Supabase project"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of the application being built"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, **kwargs) -> str:
        """Generate setup guide for user"""

        guide = f"""
# Supabase Setup Guide for {app_name}

I'll guide you through setting up Supabase. **You'll do this in your browser** - I'll just provide the steps!

## 📋 Step 1: Create Supabase Project

1. Go to: https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - **Name**: {app_name}
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create Project" (takes ~2 minutes)

**⏳ Wait for project to be ready...**

---

## 🔑 Step 2: Get Your API Keys

Once your project is ready:

1. Go to: **Project Settings** → **API**
2. Copy these values (you'll need them):

   ```
   Project URL: https://xxxxx.supabase.co
   anon public key: eyJhbG...
   service_role key: eyJhbG... (keep secret!)
   ```

3. Save them to your `.env` file:

   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbG...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbG...  # Server-only!
   ```

---

## ✅ Next Steps

Once you have your Supabase project ready, tell me:

"I've created my Supabase project, here are my keys"

Then I'll:
1. Generate the database schema (SQL migrations)
2. Show you how to run them in the SQL Editor
3. Configure authentication
4. Set up Row Level Security

**Ready to continue?**
"""
        return guide


class SupabaseSchemaGuideTool(Tool):
    """Generate SQL schema and guide user to apply it"""

    name: str = "supabase_schema_guide"
    description: str = "Generate database schema SQL and guide user to apply it in Supabase dashboard"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "tables": {
                "type": "array",
                "description": "List of tables needed (e.g., ['users', 'posts', 'subscriptions'])",
                "items": {"type": "string"}
            },
            "has_payments": {
                "type": "boolean",
                "description": "Whether the app needs Stripe payments integration"
            }
        },
        "required": ["tables"]
    }

    async def execute(self, tables: list[str], has_payments: bool = False, **kwargs) -> str:
        """Generate schema and instructions"""

        # Generate basic schema
        sql_migration = """-- Migration: Initial Schema
-- Created: {timestamp}
-- Run this in: Supabase Dashboard → SQL Editor → New Query

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

"""

        # Profiles table (always needed)
        sql_migration += """
-- User Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Trigger to create profile on signup
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

        # Add payment tables if needed
        if has_payments:
            sql_migration += """
-- Subscriptions Table (synced with Stripe)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    stripe_price_id TEXT,
    status TEXT,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscription"
    ON public.subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Products Table
CREATE TABLE IF NOT EXISTS public.products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    stripe_product_id TEXT UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Products are viewable by everyone"
    ON public.products FOR SELECT
    USING (active = true);

-- Prices Table
CREATE TABLE IF NOT EXISTS public.prices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    stripe_price_id TEXT UNIQUE,
    interval TEXT CHECK (interval IN ('month', 'year')),
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'usd',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Prices are viewable by everyone"
    ON public.prices FOR SELECT
    USING (active = true);

"""

        guide = f"""
# Database Schema Setup

I've generated the SQL schema for your app. **You'll run this in Supabase** - here's how:

## 📝 Step 1: Copy the SQL

Copy this entire SQL script:

```sql
{sql_migration}
```

## 🚀 Step 2: Run in Supabase

1. Go to your Supabase Dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Paste the SQL above
5. Click **Run** (bottom right)

**You should see:** "Success. No rows returned"

## ✅ Step 3: Verify

1. Click **Table Editor** in sidebar
2. You should see these tables:
   - ✅ profiles
{"   - ✅ subscriptions" if has_payments else ""}
{"   - ✅ products" if has_payments else ""}
{"   - ✅ prices" if has_payments else ""}

## 🔒 Security Features Included

- ✅ Row Level Security (RLS) enabled on all tables
- ✅ Users can only access their own data
- ✅ Auto-create profile on signup
- ✅ Public products/prices are readable by everyone

## 💡 What This Does

- **profiles**: Stores user metadata (linked to auth.users)
- **RLS policies**: Ensures users can't access other users' data
- **Trigger**: Auto-creates profile when user signs up
{"- **subscriptions**: Syncs with Stripe subscription status" if has_payments else ""}
{"- **products/prices**: Your subscription tiers" if has_payments else ""}

**Done? Tell me when the tables are created!**
"""

        return guide


class SupabaseAuthGuideTool(Tool):
    """Guide user to configure authentication in Supabase"""

    name: str = "supabase_auth_guide"
    description: str = "Guide user to configure authentication providers in Supabase dashboard"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "providers": {
                "type": "array",
                "description": "Auth providers to enable (e.g., ['email', 'google', 'github'])",
                "items": {"type": "string"}
            }
        },
        "required": []
    }

    async def execute(self, providers: list[str] = None, **kwargs) -> str:
        """Generate auth setup guide"""

        if not providers:
            providers = ['email']

        guide = """
# Authentication Setup Guide

Let's configure authentication in your Supabase project!

## 📧 Step 1: Email Authentication (Basic)

1. Go to: **Authentication** → **Providers** in Supabase Dashboard
2. Find **Email** provider
3. **Enable** it (should be on by default)
4. Configuration:
   - ✅ Enable email confirmations (recommended)
   - ✅ Enable secure email change (recommended)

"""

        if 'google' in providers:
            guide += """
## 🔐 Step 2: Google OAuth (Optional)

1. Go to: https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - **Application type**: Web application
   - **Authorized redirect URIs**: Add this (from Supabase):
     ```
     https://<your-project>.supabase.co/auth/v1/callback
     ```
5. Copy **Client ID** and **Client Secret**
6. In Supabase Dashboard:
   - Go to **Authentication** → **Providers**
   - Find **Google**
   - Enable it
   - Paste Client ID and Client Secret
   - Save

"""

        if 'github' in providers:
            guide += """
## 🐙 Step 3: GitHub OAuth (Optional)

1. Go to: https://github.com/settings/developers
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: Your App Name
   - **Homepage URL**: https://your-domain.com
   - **Authorization callback URL**: (get from Supabase):
     ```
     https://<your-project>.supabase.co/auth/v1/callback
     ```
4. Create app and copy **Client ID** and **Client Secret**
5. In Supabase Dashboard:
   - Go to **Authentication** → **Providers**
   - Find **GitHub**
   - Enable it
   - Paste Client ID and Client Secret
   - Save

"""

        guide += """
## ⚙️ Step 4: Email Templates (Optional but Recommended)

Customize your auth emails:

1. Go to **Authentication** → **Email Templates**
2. Customize these templates:
   - **Confirm signup**: Welcome email
   - **Magic Link**: Passwordless login
   - **Reset Password**: Password recovery

**Pro tip**: Add your branding and app name!

---

## ✅ Testing Authentication

Once set up, test it:

1. Go to **Authentication** → **Users**
2. Click **Add user** → **Create new user**
3. Enter an email and password
4. User should appear in the list!

**Ready to continue with the frontend integration?**
"""

        return guide
