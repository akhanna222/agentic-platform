"""
Stripe payment integration tools
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from app.config import get_config
from app.tools.base import Tool


class StripeSetupTool(Tool):
    """
    Set up Stripe products and prices
    """

    name: str = "stripe_setup"
    description: str = "Create Stripe products and subscription prices for a SaaS app."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Name of your SaaS product",
            },
            "create_basic_plan": {
                "type": "boolean",
                "description": "Create a basic/starter plan",
                "default": True,
            },
            "basic_price": {
                "type": "integer",
                "description": "Basic plan price in cents (e.g., 900 for $9)",
                "default": 900,
            },
            "create_pro_plan": {
                "type": "boolean",
                "description": "Create a pro/premium plan",
                "default": True,
            },
            "pro_price": {
                "type": "integer",
                "description": "Pro plan price in cents (e.g., 2900 for $29)",
                "default": 2900,
            },
        },
        "required": ["product_name"],
    }

    async def execute(
        self,
        product_name: str,
        create_basic_plan: bool = True,
        basic_price: int = 900,
        create_pro_plan: bool = True,
        pro_price: int = 2900,
    ) -> str:
        """
        Set up Stripe products

        Args:
            product_name: Product name
            create_basic_plan: Create basic plan
            basic_price: Basic plan price in cents
            create_pro_plan: Create pro plan
            pro_price: Pro plan price in cents

        Returns:
            Setup instructions and code
        """
        try:
            setup_guide = f"""
## Stripe Setup Guide

### 1. Get Stripe Keys
1. Go to https://dashboard.stripe.com/apikeys
2. Copy your keys:
   - Publishable key (starts with pk_)
   - Secret key (starts with sk_)
   - Get test keys first, then live keys for production

Add to .env:
```env
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 2. Create Products (Manual Method)

Go to https://dashboard.stripe.com/products

**Basic Plan** ({basic_price / 100:.2f} USD/month):
1. Click "Add product"
2. Name: "{product_name} - Basic"
3. Pricing: Recurring, ${basic_price / 100:.2f}/month
4. Copy the Price ID (starts with price_)

**Pro Plan** ({pro_price / 100:.2f} USD/month):
1. Click "Add product"
2. Name: "{product_name} - Pro"
3. Pricing: Recurring, ${pro_price / 100:.2f}/month
4. Copy the Price ID

Add to .env:
```env
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
```

### 3. Or Use Stripe CLI/API (Automated)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Create product and prices
stripe products create \\
  --name "{product_name} - Basic" \\
  --description "Basic plan"

stripe prices create \\
  --unit-amount {basic_price} \\
  --currency usd \\
  --recurring interval=month \\
  --product <product_id>
```

### 4. Next Steps
After setup, use:
- stripe_create_checkout to generate checkout sessions
- stripe_webhook_handler to sync subscription state
"""

            # Save config template
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            stripe_config = workspace / "stripe_config.json"

            config_data = {
                "product_name": product_name,
                "plans": {
                    "basic": {
                        "name": f"{product_name} - Basic",
                        "price": basic_price,
                        "interval": "month",
                    }
                    if create_basic_plan
                    else None,
                    "pro": {
                        "name": f"{product_name} - Pro",
                        "price": pro_price,
                        "interval": "month",
                    }
                    if create_pro_plan
                    else None,
                },
            }

            with open(stripe_config, "w") as f:
                json.dump(config_data, f, indent=2)

            return setup_guide

        except Exception as e:
            logger.error(f"Stripe setup error: {str(e)}")
            return f"Error: {str(e)}"


class StripeCheckoutCodeTool(Tool):
    """
    Generate Stripe Checkout implementation code
    """

    name: str = "stripe_checkout_code"
    description: str = "Generate server-side code for creating Stripe Checkout sessions."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "framework": {
                "type": "string",
                "description": "Backend framework",
                "enum": ["nextjs", "express", "fastapi"],
                "default": "nextjs",
            },
            "success_url": {
                "type": "string",
                "description": "URL to redirect after successful payment",
                "default": "/dashboard",
            },
            "cancel_url": {
                "type": "string",
                "description": "URL to redirect if payment cancelled",
                "default": "/pricing",
            },
        },
        "required": [],
    }

    async def execute(
        self,
        framework: str = "nextjs",
        success_url: str = "/dashboard",
        cancel_url: str = "/pricing",
    ) -> str:
        """
        Generate checkout code

        Args:
            framework: Backend framework
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL

        Returns:
            Implementation code
        """
        try:
            if framework == "nextjs":
                code = f'''
## Next.js API Route for Stripe Checkout

Create: `app/api/create-checkout/route.ts`

```typescript
import {{ NextRequest, NextResponse }} from 'next/server';
import Stripe from 'stripe';
import {{ createClient }} from '@supabase/supabase-js';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {{
  apiVersion: '2024-12-18.acacia',
}});

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(request: NextRequest) {{
  try {{
    const {{ priceId, userId }} = await request.json();

    // Verify user is authenticated
    const {{ data: {{ user }} }} = await supabase.auth.getUser(userId);
    if (!user) {{
      return NextResponse.json(
        {{ error: 'Unauthorized' }},
        {{ status: 401 }}
      );
    }}

    // Create Checkout Session
    const session = await stripe.checkout.sessions.create({{
      customer_email: user.email,
      client_reference_id: user.id,
      line_items: [
        {{
          price: priceId,
          quantity: 1,
        }},
      ],
      mode: 'subscription',
      success_url: `${{process.env.APP_URL}}{success_url}?session_id={{{{CHECKOUT_SESSION_ID}}}}`,
      cancel_url: `${{process.env.APP_URL}}{cancel_url}`,
      metadata: {{
        userId: user.id,
      }},
    }});

    return NextResponse.json({{ url: session.url }});
  }} catch (error: any) {{
    console.error('Checkout error:', error);
    return NextResponse.json(
      {{ error: error.message }},
      {{ status: 500 }}
    );
  }}
}}
```

## Client-Side Usage

```typescript
'use client';

import {{ useState }} from 'react';

export function PricingCard({{ priceId }}: {{ priceId: string }}) {{
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {{
    setLoading(true);
    try {{
      const response = await fetch('/api/create-checkout', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          priceId,
          userId: 'current-user-id', // Get from Supabase auth
        }}),
      }});

      const {{ url }} = await response.json();
      if (url) {{
        window.location.href = url; // Redirect to Stripe Checkout
      }}
    }} catch (error) {{
      console.error('Error:', error);
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <button
      onClick={{handleCheckout}}
      disabled={{loading}}
      className="btn-primary"
    >
      {{loading ? 'Loading...' : 'Subscribe Now'}}
    </button>
  );
}}
```

## Environment Variables Needed

```env
STRIPE_SECRET_KEY=sk_test_...
APP_URL=http://localhost:3000  # or your deployed URL
NEXT_PUBLIC_SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```
'''

            else:
                code = f"Framework '{framework}' code generation not yet implemented. Use 'nextjs' for now."

            # Save code to workspace
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            code_file = workspace / f"stripe_checkout_{framework}.md"

            with open(code_file, "w") as f:
                f.write(code)

            return code + f"\n\n💾 Saved to: {code_file}"

        except Exception as e:
            logger.error(f"Checkout code error: {str(e)}")
            return f"Error: {str(e)}"


class StripeWebhookCodeTool(Tool):
    """
    Generate Stripe Webhook handler code
    """

    name: str = "stripe_webhook_code"
    description: str = "Generate webhook handler code to sync Stripe events with Supabase database."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "framework": {
                "type": "string",
                "description": "Backend framework",
                "enum": ["nextjs", "express"],
                "default": "nextjs",
            }
        },
        "required": [],
    }

    async def execute(self, framework: str = "nextjs") -> str:
        """
        Generate webhook code

        Args:
            framework: Backend framework

        Returns:
            Implementation code
        """
        try:
            code = '''
## Stripe Webhook Handler

Create: `app/api/webhooks/stripe/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createClient } from '@supabase/supabase-js';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',
});

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    // Verify webhook signature
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err: any) {
    console.error('Webhook signature verification failed:', err.message);
    return NextResponse.json({ error: err.message }, { status: 400 });
  }

  // Handle events
  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        await handleCheckoutCompleted(session);
        break;
      }

      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionUpdate(subscription);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionDeleted(subscription);
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentSucceeded(invoice);
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentFailed(invoice);
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error: any) {
    console.error('Webhook handler error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

async function handleCheckoutCompleted(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.userId || session.client_reference_id;
  if (!userId) return;

  // Get subscription details
  const subscriptionId = session.subscription as string;
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);

  await upsertSubscription(userId, subscription);
}

async function handleSubscriptionUpdate(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.userId;
  if (!userId) {
    console.error('No userId in subscription metadata');
    return;
  }

  await upsertSubscription(userId, subscription);
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  const { error } = await supabase
    .from('subscriptions')
    .update({
      status: 'canceled',
      updated_at: new Date().toISOString(),
    })
    .eq('id', subscription.id);

  if (error) console.error('Error updating subscription:', error);
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  const subscription = invoice.subscription as string;
  const customerId = invoice.customer as string;

  // Record payment
  const { error } = await supabase.from('payments').insert({
    id: invoice.payment_intent as string,
    subscription_id: subscription,
    amount: invoice.amount_paid,
    currency: invoice.currency,
    status: 'succeeded',
  });

  if (error) console.error('Error recording payment:', error);
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  // Handle failed payment (e.g., send notification)
  console.log('Payment failed for invoice:', invoice.id);
}

async function upsertSubscription(userId: string, subscription: Stripe.Subscription) {
  const priceId = subscription.items.data[0]?.price.id;

  const { error } = await supabase
    .from('subscriptions')
    .upsert({
      id: subscription.id,
      user_id: userId,
      status: subscription.status,
      plan_id: priceId,
      current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
      current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
      cancel_at_period_end: subscription.cancel_at_period_end,
      updated_at: new Date().toISOString(),
    });

  if (error) {
    console.error('Error upserting subscription:', error);
    throw error;
  }

  // Update entitlements based on plan
  await updateEntitlements(userId, priceId);
}

async function updateEntitlements(userId: string, priceId: string) {
  // Map price IDs to features
  const features = priceId === process.env.STRIPE_PRICE_PRO
    ? ['api_access', 'premium_support', 'advanced_features']
    : ['basic_features'];

  // Upsert entitlements
  for (const feature of features) {
    await supabase
      .from('entitlements')
      .upsert({
        user_id: userId,
        feature_key: feature,
        enabled: true,
      });
  }
}
```

## Setup Webhook in Stripe Dashboard

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter: `https://your-domain.com/api/webhooks/stripe`
4. Select events:
   - checkout.session.completed
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
5. Copy the webhook signing secret
6. Add to .env: `STRIPE_WEBHOOK_SECRET=whsec_...`

## Local Testing with Stripe CLI

```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

This will give you a webhook secret for testing.
'''

            # Save code
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            code_file = workspace / "stripe_webhook_handler.md"

            with open(code_file, "w") as f:
                f.write(code)

            return code + f"\n\n💾 Saved to: {code_file}"

        except Exception as e:
            logger.error(f"Webhook code error: {str(e)}")
            return f"Error: {str(e)}"
