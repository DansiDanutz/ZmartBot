# Your Step-by-Step Guide to Building the Zmarty Trading System

Hello! I'm Manus, and I'm here to help you bring your Zmarty Chat and Zmarty Trading projects to life. You've already done an incredible amount of work building the foundational components of your system. Now, let's connect them to create the powerful, independent, and profitable trading assistant you envision.

The document you provided is an excellent blueprint created by a senior developer. It lays out a clear and robust architecture for your Zmarty Control Plane. My goal is to walk you through this blueprint step-by-step, providing the explanations and guidance you need to implement it successfully.

This guide will be your comprehensive resource for building, deploying, and monitoring your Zmarty system. We'll cover everything from the overall architecture to the nitty-gritty details of implementation.

Let's get started!

## 1. System Architecture Overview

First, let's understand the big picture. The blueprint you received outlines a professional, scalable, and robust architecture. Here's a breakdown of the components and how they work together. We can think of this as the 'Zmarty Control Plane'.

| Component             | Responsibility                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**         | Your user interface, built with a framework like React and hosted on**Netlify**. This is what your users will interact with.                 |
| **Supabase A (Chat)** | This is your primary user-facing database. It handles user authentication, profiles, subscription tiers, credits, and user-selected crypto symbols. |
| **Supabase B (Trading)** | This is your backend trading database. It stores trading data, indicators, risk metrics, liquidation clusters, and trading signals.          |
| **Database Webhook**  | This is a crucial link between your two Supabase projects. When a user adds a crypto symbol in Supabase A, a webhook automatically updates Supabase B. |
| **Queues (pgmq)**     | A message queue system within Supabase B that helps manage and process asynchronous tasks like fetching data and calculating trading signals.      |
| **Schedules (pg_cron)** | A cron job scheduler within Supabase B that runs periodic tasks, such as re-calculating win rates.                                         |
| **Render**            | This is where your backend logic lives. You'll have two services running on Render:                                                         |
| &nbsp;&nbsp;&nbsp;&nbsp;*orchestrator-api* | A web service that handles user requests from the frontend, communicates with the AI models, and manages user credits.                      |
| &nbsp;&nbsp;&nbsp;&nbsp;*orchestrator-worker* | A background worker that processes tasks from the message queues, such as ingesting data from your crypto data sources and computing signals. |
| **ElevenLabs**        | Provides the text-to-speech functionality for Zmarty's voice responses.                                                                     |

### Data Flow

Here’s how data flows through the system:

1.  A user interacts with the **Frontend** (on Netlify).
2.  The user's actions (like adding a symbol) are stored in **Supabase A**.
3.  A **Database Webhook**in Supabase A triggers an Edge Function in**Supabase B** to keep the `watchers` table in sync.
4.  The **orchestrator-worker**(on Render) is constantly pulling data from Cryptometer and King Fisher, and it uses the message**Queues** in Supabase B to process this data.
5.  The worker calculates trading signals and stores them in **Supabase B**.
6.  When a user sends a message in the chat, the **Frontend**sends a request to the**orchestrator-api** (on Render).
7.  The **orchestrator-api**validates the user, fetches the latest signals from**Supabase B**, sends the data to the AI models (Grok, GPT, or Claude) for analysis, and then charges the user's credits in **Supabase A**.
8.  The AI's response is sent back to the user through the **Frontend**, with an optional voice response from **ElevenLabs**.

This architecture is designed to be **decoupled**, meaning each component can be developed, deployed, and scaled independently. This is a best practice for building complex systems.

## 2. Your Current Assets and What's Missing

Based on your description, you've already built impressive foundational components:

### ✅ What You Have
- **Two Supabase projects** with no errors
- **Cryptometer integration** with 21 indicators working correctly
- **King Fisher liquidation clusters** implemented and ready
- **Risk Metric** system integrated into Supabase
- **Google Cloud** email validation and callbacks
- **RESEND SMTP** for email functionality
- **Render and Netlify Pro accounts** ready for deployment

### 🔧 What We Need to Connect
- **Database webhook** between Supabase A and B
- **Message queues** (pgmq) in Supabase B
- **Orchestrator services** on Render (API + Worker)
- **AI model routing** with credit management
- **Monitoring and observability** system
- **Frontend integration** with the backend API

## 3. Step-by-Step Implementation Plan

Let's break this down into manageable phases. Each phase builds on the previous one, so you can test and verify as you go.

### Phase 1: Database Setup and Schema (Day 1)

#### Step 1.1: Create the Blueprint Folder

First, we need to create a structured blueprint that Cursor and Claude can use as their source of truth.

In your project root directory, create this folder structure:

```bash
docs/
└─ zmarty-blueprint/
   ├─ 00-OVERVIEW.md
   ├─ 10-TASKLIST.md
   ├─ 20-SCHEMA-SUPABASE-A.sql
   ├─ 21-SCHEMA-SUPABASE-B.sql
   ├─ 30-EDGE-FUNCTION-watchers-upsert.md
   ├─ 40-ORCHESTRATOR-API.md
   ├─ 41-ORCHESTRATOR-WORKER.md
   ├─ 50-ENV.sample
   ├─ 60-CREDITS-PRICING.md
   ├─ specs/API-CONTRACTS.md
   └─ runbooks/ONCALL.md
```

#### Step 1.2: Apply Database Schemas

You'll need to run SQL scripts in both of your Supabase projects. The blueprint provides the exact SQL you need:

**For Supabase A (Chat Project):**

- Add `user_symbols` table to track which crypto symbols each user is watching
- Add `credits_ledger` table to track credit usage and charges
- Add `credit_balance` view for easy balance checking
- Set up Row Level Security (RLS) policies

**For Supabase B (Trading Project):**

- Add `watchers` table (mirrors user_symbols from Supabase A)
- Add `indicators` table for storing Cryptometer data
- Add `risk_metric` table for your risk calculations
- Add `liq_clusters` table for King Fisher data
- Add `signals` table for trading signals
- Add `win_rate` table for performance tracking
- Enable pgmq extension for message queues
- Enable pg_cron extension for scheduled tasks

#### Step 1.3: Set Up Message Queues

In Supabase B, you'll create three message queues:

- `ingest_indicators`: For processing incoming market data
- `compute_signals`: For calculating trading signals
- `compute_winrate`: For updating performance metrics

### Phase 2: Database Webhook Connection (Day 1)

#### Step 2.1: Create Edge Function in Supabase B

This function will receive webhook calls from Supabase A whenever a user adds, updates, or removes a crypto symbol.

**Key responsibilities:**

- Verify the webhook is authentic (HMAC signature)
- Update the `watchers` table in Supabase B
- Respond quickly (under 1 second)

#### Step 2.2: Configure Webhook in Supabase A

Set up a database webhook that triggers whenever the `user_symbols` table changes:

- **Trigger**: INSERT, UPDATE, DELETE on `public.user_symbols`
- **Destination**: Your Supabase B Edge Function URL
- **Security**: HMAC signature for verification

### Phase 3: Render Services Setup (Day 1-2)

#### Step 3.1: Orchestrator API Service

This is your main backend API that handles user requests.

**Key endpoints:**

- `POST /chat`: Main chat interface with AI models
- `GET /healthz`: Health check for monitoring

**Key responsibilities:**

- Verify user authentication (JWT from Supabase A)
- Fetch user's symbols and latest signals
- Route requests to appropriate AI model (Grok default, GPT/Claude as fallback)
- Charge user credits after each interaction
- Return AI response (text and optional audio URL)

#### Step 3.2: Orchestrator Worker Service

This is your background worker that processes data and calculations.

**Key responsibilities:**

- **Ingest indicators**: Pull data from Cryptometer API
- **Ingest liquidation data**: Pull data from King Fisher
- **Compute signals**: Analyze all data to generate trading signals
- **Compute win rates**: Calculate performance metrics
- **Risk management**: Apply your "doubling" strategy with safety guardrails

### Phase 4: AI Model Integration and Credit System (Day 2)

#### Step 4.1: Model Router Implementation

Create a smart routing system for AI models:

| Model | Use Case | Cost | Priority |
|-------|----------|------|----------|
| **Grok** | Default for most requests | Low | Primary |
| **GPT-4** | Complex analysis, fallback | Medium | Secondary |
| **Claude** | Detailed explanations, fallback | Medium | Secondary |

#### Step 4.2: Credit Management System

Implement a fair and profitable credit system:

```bash
Credit Calculation = ceil((input_tokens/1000) * input_rate + (output_tokens/1000) * output_rate + minimum_charge)
```

**Example pricing structure:**

- Grok: 1 credit per 1k input tokens, 4 credits per 1k output tokens, 1 credit minimum
- GPT: 3 credits per 1k input tokens, 10 credits per 1k output tokens, 2 credits minimum
- Claude: 3 credits per 1k input tokens, 10 credits per 1k output tokens, 2 credits minimum
- Data requests: 1 credit flat rate

### Phase 5: Frontend Integration (Day 2)

#### Step 5.1: Chat Interface

Connect your frontend to the orchestrator API:

- Send user messages with JWT authentication
- Stream responses in real-time
- Display trading signals and analysis
- Handle voice responses from ElevenLabs

#### Step 5.2: User Dashboard

Create interfaces for:

- Managing watched crypto symbols
- Viewing credit balance and usage history
- Displaying trading signals and win rates
- Account settings and subscription management

### Phase 6: Monitoring and Observability (Day 3)

Once your system is running, you need to be able to see what's happening under the hood. This is crucial for debugging, ensuring reliability, and understanding how your system is performing.

#### Step 6.1: Admin Dashboard

Create a simple admin page that gives you a real-time view of your system's health. This page should display:

- **Queue Depth**: How many jobs are waiting in your pgmq queues? A high number might indicate a bottleneck.
- **Cron Status**: When did your scheduled tasks last run, and were they successful?
- **Recent Errors**: A log of the latest errors from your API and worker services.

#### Step 6.2: Logging

Implement structured logging in your Render services. For each log entry, include important context like:

- `symbol`
- `timeframe`
- `job_name`
- `duration_ms`
- `queue_depth`

This will make it much easier to search and filter your logs when you're trying to diagnose a problem.

#### Step 6.3: Health Checks

Your `GET /healthz` endpoint is your first line of defense. It should check:

- **Database Connectivity**: Can the API service connect to both Supabase A and Supabase B?
- **Provider Reachability**: Can the API service connect to the APIs for Grok, OpenAI, Anthropic, and ElevenLabs?

You can set up an automated uptime checker (like UptimeRobot or a similar service) to ping this endpoint every few minutes and alert you if it goes down.

## 4. How to Use Cursor and Claude for Development

The blueprint you have is designed to be used with an AI-powered code editor like Cursor, with Claude as the AI model. This approach allows you to leverage the power of AI to write the code for you, while you maintain control and review every change. Here’s how to do it effectively.

### A. Give the AI the Right Context

The `docs/zmarty-blueprint/` folder is your single source of truth. Before you start coding, you need to make sure the AI has this context.

1.  Open your project in Cursor.
2.  Open the `00-OVERVIEW.md` and `10-TASKLIST.md` files.
3.  In the chat panel, attach the entire `docs/zmarty-blueprint/` folder as context.
4.  Start the chat with this instruction:

    > “Use the files in `docs/zmarty-blueprint/` as the source of truth. Before coding, summarize your plan in bullets and list exactly which files you will create or edit. Ask for confirmation if your plan changes.”

### B. Generate Code in Safe, Reviewable Chunks

Don't ask the AI to build the whole thing at once. Instead, give it small, specific tasks that correspond to the implementation plan. Use Cursor’s “Edit / Diff” flow to review and accept or reject each change.

Here are the prompts you can use, taken directly from the senior developer's notes:

*   **Prompt 1 (Database Migrations):**

    > “Create migration files that apply `20-SCHEMA-SUPABASE-A.sql` and `21-SCHEMA-SUPABASE-B.sql`. Put them under `/supabase/chat/migrations/` and `/supabase/trading/migrations/`. Do not change other files. Show the exact SQL content taken from the blueprint.”

*   **Prompt 2 (Edge Function):**

    > “Generate Supabase B Edge Function `watchers-upsert` per `30-EDGE-FUNCTION-watchers-upsert.md`. Create `/supabase/trading/functions/watchers-upsert/index.ts` with HMAC verification, upsert/delete logic, and a 1‑second timeout budget. Show the full file.”

*   **Prompt 3 (Render Services Scaffolding):**

    > “Scaffold two Node/TypeScript services: `/services/orchestrator-api` and `/services/orchestrator-worker` following `40-ORCHESTRATOR-API.md` and `41-ORCHESTRATOR-WORKER.md`. Use pnpm workspaces and TypeScript. Add minimal endpoints: `/chat` and `/healthz`. In the worker, add consumers for `ingest_indicators`, `compute_signals`, and `compute_winrate` with placeholder handlers. Read env from `50-ENV.sample`. Output a diff and a short README for each service.”

*   **Prompt 4 (Model Router & Credits):**

    > “Implement a simple model router: Grok default; GPT/Claude fallback when asked, with a price cap. After each call, write a row to Supabase A `credits_ledger` using the formula in `60-CREDITS-PRICING.md`. Avoid sending service keys to the browser.”

*   **Prompt 5 (Frontend Hook-up):**

    > “Add a small client in the frontend that hits `/chat` with a user JWT, streams text, and optionally fetches ElevenLabs audio if `audioUrl` is returned.”

### C. Keep the AI on a Tight Leash

To prevent the AI from making unexpected changes, start your first chat session with these “house rules”:

> **Rules for you (Claude):**
> 1.  Only create/edit files you list first.
> 2.  Work in small, PR-sized steps (≤ 8 files). Always show a diff.
> 3.  Use the blueprint docs as the authoritative spec.
> 4.  Never push service keys to the client.
> 5.  After each step, print a brief test plan (describing how to run and verify).
> 6.  If you’re not sure, ask before touching unrelated files.

This disciplined approach ensures that you are always in control of the development process.

## 5. First Local Run Sequence (Testing Your Setup)

After you've generated the code, it's time to test it locally to make sure everything is working as expected. Follow this sequence:

1.  **Apply Database Migrations**: Run the SQL migration files you created in your Supabase projects. You can do this through the Supabase SQL editor in the dashboard or using the Supabase CLI.

2.  **Deploy Edge Function**: Deploy the `watchers-upsert` function in Supabase B. Make sure to set the `WEBHOOK_SECRET` environment variable in the function's settings.

3.  **Configure Webhook**: In Supabase A, create the database webhook on the `public.user_symbols` table. Point it to your Supabase B function's URL and configure the HMAC header with the same secret.

4.  **Deploy Render Services**: Deploy the `orchestrator-api` and `orchestrator-worker` services on Render. Set all the required environment variables from your `50-ENV.sample` file.

5.  **End-to-End Test 1 (Webhook)**: In your frontend application, log in as a user and add a new crypto symbol to your watchlist. Verify that the corresponding entry is created in the `watchers` table in Supabase B.

6.  **End-to-End Test 2 (Worker)**: Manually enqueue a test job in the `ingest_indicators` queue in Supabase B. You can do this from the Supabase SQL editor. Verify that the worker picks up the job, writes to the `indicators` table, and triggers the `compute_signals` job.

7.  **End-to-End Test 3 (Chat)**: From your frontend, send a chat message. Verify that you get a response from the AI and that a new row is added to the `credits_ledger` table in Supabase A.

## 6. Tips for Productive AI-Powered Development

- **Pin the Blueprint**: In Cursor, you can pin the `docs/zmarty-blueprint/` folder to every new chat. This ensures the AI always has the necessary context without you having to re-attach it every time.
- **Plan First, Then Code**: Always ask the AI for a plan before it starts writing code. This gives you a chance to catch any misunderstandings early.
- **Small, Atomic Commits**: Break down the work into small, logical chunks. This makes it easier to review changes and roll them back if something goes wrong.
- **Test After Each Change**: After each change is accepted, run the small test plan that the AI proposes. This helps you catch bugs immediately.
- **Be Specific**: If the AI's output isn't what you expected, don't be afraid to correct it. Paste the relevant section from the blueprint and say, “Follow this verbatim.”

## 7. Using the Command Line with Claude Code

If you prefer working in the terminal, you can use Claude Code directly from the command line within Cursor's integrated terminal. The workflow is very similar:

1.  Open your project in Cursor.
2.  Open the integrated terminal.
3.  Run Claude Code tasks from the command line.

The blueprint folder works just the same. Claude Code will read the local context and propose changes as diffs. The core workflow remains: **Plan → Diff → Accept → Test**.

## Conclusion

You have a solid plan and a powerful set of tools at your disposal. By following this step-by-step guide and leveraging the blueprint provided, you can systematically connect all the pieces of your Zmarty project.

Remember to work in small, iterative steps, and test as you go. This is the key to managing complexity and building a robust, reliable system.

I am here to help you at every step. If you have any questions or get stuck, don't hesitate to ask. Let's build this!
