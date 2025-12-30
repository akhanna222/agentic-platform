# FullStack Ship Agent - Complete Guide

The **FullStack Ship Agent** is a specialized agent that builds and deploys complete SaaS applications following the Lovable/Replit/Base44 stack.

## 🎯 What It Does

Builds a production-ready SaaS app with:
- ✅ Frontend: Next.js (React)
- ✅ Backend: Supabase (Postgres + Auth + Storage)
- ✅ Payments: Stripe (Checkout + Webhooks)
- ✅ Hosting: Replit or Vercel
- ✅ Complete automation from idea to deployed URL

## 🚀 Quick Start

### Option 1: Interactive Mode
```bash
python main.py --agent ship
```

Then describe your SaaS idea when prompted.

### Option 2: Command Line
```bash
python main.py --agent ship --prompt "Build a SaaS app for project management with team collaboration, basic plan at $9/month, pro plan at $29/month"
```

## 📋 The 6-Phase Workflow

### Phase 1: Requirements Gathering
The agent will ask you about:
- What problem does your SaaS solve?
- Who are your target users?
- What features do you need?
- What's your pricing model?

### Phase 2: Supabase Setup (Database + Auth)
The agent will:
1. Guide you to create a Supabase project
2. Generate database schema with migrations:
   - `profiles` - User metadata
   - `subscriptions` - Stripe subscription state
   - `products` / `prices` - Stripe product catalog
   - `payments` - Transaction history
   - `entitlements` - Feature flags
3. Enable Row Level Security (RLS) with policies
4. Configure authentication (email, magic link, OAuth)

**You'll need:**
- Supabase account (free tier OK)
- About 5 minutes for project creation

### Phase 3: Stripe Setup (Payments)
The agent will:
1. Guide you to get Stripe API keys
2. Help you create products and prices
3. Generate Checkout Session endpoint code
4. Generate Webhook handler code
5. Explain webhook configuration

**You'll need:**
- Stripe account (free, no credit card needed for test mode)
- About 10 minutes for setup

### Phase 4: Application Code Generation
The agent will create:
- Next.js project structure
- Auth pages (login, signup, protected routes)
- Pricing page with Stripe integration
- User dashboard with subscription management
- Environment variable templates
- All necessary API routes

**Generated files:**
- `/app/` - Next.js app router pages
- `/components/` - Reusable React components
- `/lib/supabase.ts` - Supabase client
- `/api/create-checkout/` - Stripe checkout endpoint
- `/api/webhooks/stripe/` - Stripe webhook handler
- `.env.example` - Environment variables template

### Phase 5: Deployment
The agent will provide:
- Deployment configuration files
- Step-by-step deployment guide for:
  - **Replit** (easiest, all-in-one)
  - **Vercel** (best for Next.js)
- Environment variable setup instructions
- Custom domain configuration (optional)

**Deployment takes:**
- Replit: 5-10 minutes
- Vercel: 2-5 minutes

### Phase 6: Verification & Next Steps
The agent will:
1. Verify deployment is accessible
2. Provide testing checklist:
   - ✅ Auth signup/login works
   - ✅ Database writes work
   - ✅ Stripe checkout creates session
   - ✅ Webhook endpoint responds
3. Suggest next features to build
4. Provide monitoring setup

## 🔑 Prerequisites

### Required Accounts (All Free Tier Available)

1. **Supabase** (https://supabase.com)
   - Free tier: 500MB database, 50K monthly active users
   - 2 free projects

2. **Stripe** (https://stripe.com)
   - Free test mode (no credit card needed)
   - Production mode available when ready

3. **Hosting** (choose one):
   - **Replit** (https://replit.com) - Free tier available
   - **Vercel** (https://vercel.com) - Free hobby plan (perfect for Next.js)

4. **GitHub** (https://github.com) (optional but recommended)
   - For version control and easy deployment

### Environment Variables You'll Need

The agent will help you get these, but here's the full list:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...

# App
APP_URL=https://your-app-url.com
```

## 💡 Example Use Cases

### 1. Project Management SaaS
```bash
python main.py --agent ship --prompt "Build a project management SaaS with task boards, team collaboration, and time tracking. Basic plan at $9/month, Pro plan at $29/month."
```

### 2. Content Platform
```bash
python main.py --agent ship --prompt "Create a content publishing platform where writers can create and monetize articles. Free tier with ads, Premium at $4.99/month for ad-free."
```

### 3. Analytics Dashboard
```bash
python main.py --agent ship --prompt "Build an analytics dashboard for tracking website metrics with real-time data visualization. Starter at $19/month, Business at $49/month."
```

## 🎨 What Gets Generated

### Frontend (Next.js)
- Modern, responsive UI with Tailwind CSS
- Authentication flows (login, signup, password reset)
- Pricing page with Stripe Checkout integration
- Protected dashboard routes
- Subscription management UI
- User profile management

### Backend (Supabase + Next.js API)
- PostgreSQL database with proper schema
- Row Level Security (RLS) policies
- Automatic profile creation on signup
- Stripe Checkout Session creation endpoint
- Stripe Webhook handler for subscription sync
- Subscription status queries

### Payments (Stripe)
- Product and price creation
- Checkout Session integration
- Webhook event handling:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
- Subscription state synchronization
- Payment history tracking

### Security Features
- Row Level Security (RLS) on all tables
- Server-only Stripe operations
- Webhook signature verification
- Environment variable validation
- Secure session management
- HTTPS enforcement (in production)

## 🔒 Security Best Practices (Built In)

1. **Never Expose Service Keys**
   - Service role keys stay server-side only
   - Stripe secret key never goes to client
   - Webhook secrets properly validated

2. **Row Level Security**
   - Users can only access their own data
   - Policies enforce data isolation
   - Admin access requires service role

3. **Webhook Verification**
   - All webhooks verify Stripe signatures
   - Prevents unauthorized data modifications

4. **Environment Variables**
   - Separate test and production keys
   - Never commit secrets to git
   - Platform-specific secret management

## 📈 Post-Deployment

After the agent ships your app, you can:

1. **Add Features**
   - Use the platform agent for new features
   - Use the data agent for analytics
   - Use the browser agent for integrations

2. **Scale**
   - Supabase auto-scales on paid plans
   - Vercel/Replit handle traffic automatically
   - Stripe handles unlimited transactions

3. **Monitor**
   - Supabase dashboard for DB queries
   - Stripe dashboard for payments
   - Vercel/Replit for app performance

4. **Customize**
   - All generated code is yours to modify
   - Well-organized and commented
   - Standard patterns for easy extension

## 🤝 How the Agent Helps You

### Decision Making
The agent asks clarifying questions:
- "What features are most important?"
- "What's your pricing strategy?"
- "Which hosting platform do you prefer?"

### Code Generation
Creates production-ready code:
- TypeScript for type safety
- Best practices and patterns
- Comprehensive error handling
- Clear comments and documentation

### Step-by-Step Guidance
Provides detailed instructions:
- Copy-paste ready commands
- Screenshots references (when helpful)
- Troubleshooting tips
- Links to official docs

### Validation
Verifies each phase:
- Database schema is correct
- Auth flows work properly
- Stripe integration is secure
- Deployment is successful

## 🛠️ Troubleshooting

### "Supabase project not found"
- Double-check your SUPABASE_URL
- Verify the project is created and active
- Check API keys are from the correct project

### "Stripe webhook failing"
- Verify STRIPE_WEBHOOK_SECRET is correct
- Check webhook endpoint URL is accurate
- Ensure app is deployed and accessible
- Test with `stripe listen --forward-to`

### "Build failed on deployment"
- Check all environment variables are set
- Verify Node.js version compatibility
- Review build logs for specific errors
- Ensure dependencies are in package.json

### "RLS policy blocking queries"
- Verify user is authenticated
- Check policy allows the operation
- Use service role key for admin operations
- Review Supabase logs for policy errors

## 📚 Additional Resources

### Official Documentation
- **Supabase**: https://supabase.com/docs
- **Stripe**: https://stripe.com/docs
- **Next.js**: https://nextjs.org/docs
- **Vercel**: https://vercel.com/docs
- **Replit**: https://docs.replit.com

### Helpful Guides
- [Supabase + Next.js Quickstart](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
- [Stripe Checkout Integration](https://stripe.com/docs/checkout/quickstart)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

### Community
- [Supabase Discord](https://discord.supabase.com)
- [Stripe Discord](https://discord.gg/stripe)
- [Next.js Discussions](https://github.com/vercel/next.js/discussions)

## 🎓 Learning Path

If you're new to the stack:

1. **Week 1**: Learn Next.js basics
   - React fundamentals
   - Next.js App Router
   - API routes

2. **Week 2**: Understand Supabase
   - Database basics
   - Authentication
   - Row Level Security

3. **Week 3**: Master Stripe
   - Checkout Sessions
   - Webhooks
   - Subscription management

4. **Week 4**: Deploy and iterate
   - Choose hosting platform
   - Set up CI/CD
   - Monitor and improve

The FullStack Ship Agent accelerates this process significantly!

## 💰 Cost Estimates

### Free Tier (Perfect for MVP)
- Supabase: $0 (500MB DB, 50K users)
- Stripe: $0 (test mode, production has fees)
- Vercel: $0 (hobby plan)
- **Total: $0/month**

### Growing SaaS (1,000 users)
- Supabase Pro: $25/month
- Stripe: ~2.9% + 30¢ per transaction
- Vercel Pro: $20/month (optional)
- **Total: ~$45/month + transaction fees**

### Scaling SaaS (10,000+ users)
- Supabase: Custom pricing
- Stripe: Volume discounts available
- Vercel: Enterprise plans
- **Total: Negotiate based on usage**

## 🚀 Ready to Ship?

```bash
python main.py --agent ship
```

The agent will guide you through the entire process from idea to deployed SaaS app!

---

**Built with ❤️ by the Agentic Platform**
