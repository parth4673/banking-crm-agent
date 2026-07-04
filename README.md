# 🏦 Agentic AI for Banking CRM

An **Agentic AI system** that assists Relationship Managers (RMs) in identifying high-potential customers and generating personalized outreach — built with a custom agent loop, OpenAI function calling, SQLite, and Streamlit.

---

## 📐 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    STREAMLIT CHAT UI                             │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │  RM types: "Find high-value customers for personal loan  │   │
│   │  and generate WhatsApp messages"                         │   │
│   └──────────────────────┬───────────────────────────────────┘   │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     AGENT LOOP (agent.py)                        │
│                                                                  │
│   ┌─────────┐    ┌───────────────┐    ┌──────────────────┐      │
│   │ Message  │───▶│  OpenAI LLM   │───▶│  Tool Calls?     │      │
│   │ History  │    │  (GPT-4o)     │    │                  │      │
│   └─────────┘    └───────────────┘    └────────┬─────────┘      │
│                                          Yes │        │ No       │
│                                              ▼        ▼          │
│                                     ┌──────────┐  ┌─────────┐   │
│                                     │ Execute  │  │ Return  │   │
│                                     │ Tools    │  │ Answer  │   │
│                                     └────┬─────┘  └─────────┘   │
│                                          │                       │
│                                          ▼                       │
│                                   Feed results                   │
│                                   back to LLM ──── (loop) ──┐   │
│                                                              │   │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      TOOLS LAYER                                 │
│                                                                  │
│  ┌─────────────────┐  ┌───────────────────┐  ┌──────────────┐  │
│  │ Customer Tools   │  │ Scoring Tools     │  │ Product Tools│  │
│  │                  │  │                   │  │              │  │
│  │ • get_high_value │  │ • score_conversion│  │ • recommend  │  │
│  │ • get_profile    │  │   _likelihood     │  │   _products  │  │
│  │ • search         │  │                   │  │ • get_catalog│  │
│  └────────┬─────────┘  └─────────┬─────────┘  └──────┬───────┘  │
│           │                      │                    │          │
│  ┌────────┴──────────────────────┴────────────────────┘          │
│  │                                                               │
│  │  ┌──────────────────┐                                        │
│  │  │ Message Tools    │                                        │
│  │  │                  │                                        │
│  │  │ • generate_      │                                        │
│  │  │   whatsapp_msg   │                                        │
│  │  └────────┬─────────┘                                        │
│  │           │                                                   │
└──┼───────────┼───────────────────────────────────────────────────┘
   │           │
   ▼           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   SQLite DATABASE                                │
│                                                                  │
│  ┌───────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ customers │ │ transactions │ │ products │ │ interactions │  │
│  │ (50 rows) │ │ (~1300 rows) │ │ (8 rows) │ │ (~125 rows)  │  │
│  └───────────┘ └──────────────┘ └──────────┘ └──────────────┘  │
│                                                                  │
│  ┌───────────────────┐                                          │
│  │ customer_products │                                          │
│  │ (~100 rows)       │                                          │
│  └───────────────────┘                                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Execution Flow

Here's what happens when an RM asks: *"Find high-value customers likely to convert for a personal loan and generate WhatsApp messages"*

```
Step 1 ─── RM sends message via Streamlit chat
                │
Step 2 ─── Agent sends message + tool definitions to OpenAI
                │
Step 3 ─── LLM decides: "I need to find high-value customers first"
           └── Calls: get_high_value_customers(min_income=500000, min_credit_score=700)
                │
Step 4 ─── Agent executes tool, gets 15 matching customers
           └── Feeds results back to LLM
                │
Step 5 ─── LLM decides: "Now I'll score these for personal loan conversion"
           └── Calls: score_conversion_likelihood(customer_ids="CUST0001,...", product_type="Personal Loan")
                │
Step 6 ─── Agent executes scoring, returns ranked list with explanations
           └── Feeds results back to LLM
                │
Step 7 ─── LLM decides: "Top 3 are HOT leads. Let me generate messages."
           └── Calls: generate_whatsapp_message(customer_id="CUST0023", product_name="Personal Loan")
           └── Calls: generate_whatsapp_message(customer_id="CUST0007", product_name="Personal Loan")
           └── Calls: generate_whatsapp_message(customer_id="CUST0041", product_name="Personal Loan")
                │
Step 8 ─── Agent executes message generation for each customer
           └── Feeds all results back to LLM
                │
Step 9 ─── LLM composes final response summarizing:
           • Customers found and why they qualify
           • Conversion scores with explanations
           • Personalized WhatsApp messages ready to send
                │
Step 10 ── Response displayed in Streamlit with tool trace
```

---

## 🔧 Tool Design & Usage

### 7 Tools in 4 Categories

| Tool | Category | Purpose | Inputs | Output |
|------|----------|---------|--------|--------|
| `get_high_value_customers` | Discovery | Filter customers by income, balance, credit score, segment, city | Filters + limit | Customer list with transaction stats |
| `get_customer_profile` | Discovery | Deep-dive into one customer | customer_id | Full profile + products + interactions |
| `search_customers` | Discovery | Text search across customer fields | query string | Matching customers |
| `score_conversion_likelihood` | Scoring | Heuristic scoring for product conversion | customer_ids, product_type | Scored + ranked list with reasons |
| `recommend_products` | Products | Match customer to suitable products | customer_id | Ranked product recommendations |
| `get_product_catalog` | Products | List all available products | — | Product catalog |
| `generate_whatsapp_message` | Outreach | Create personalized WhatsApp message | customer_id, product, tone, language | Ready-to-send message |

### Scoring Model (Heuristic, 0–100)

| Factor | Points | Logic |
|--------|--------|-------|
| Income adequacy | 0–20 | Tiered by income bracket |
| Credit score | 0–20 | 800+ = 20pts, 720+ = 16pts, etc. |
| Account balance | 0–15 | Higher balance = more points |
| Transaction activity | 0–15 | More active = more engaged |
| Relationship vintage | 0–10 | Longer = more trust |
| No existing similar product | 0–10 | Gap = opportunity |
| Spending pattern signals | 0–10 | Cashflow analysis |

**Tiers**: HOT (75+), WARM (55–74), MILD (35–54), COLD (<35)

---

## 🎯 Key Design Decisions

1. **Custom agent loop over LangChain**: Built the tool-calling loop from scratch to demonstrate understanding of agentic patterns. Every line of orchestration is visible and debuggable.

2. **OpenAI function calling as the reasoning engine**: The LLM decides which tools to call and in what order. The agent just executes and feeds results back. This gives the system flexibility to handle diverse RM queries.

3. **SQLite with realistic data**: Instead of mock JSON files, we use a real relational database with 50 customers, ~1300 transactions, products, and interaction history. Tools run actual SQL queries.

4. **Heuristic scoring over ML**: For a CRM demo, explainability beats accuracy. The rule-based scorer shows exactly why each customer scored high/low, which RMs need for compliance and trust.

5. **Tool registry pattern**: All tools are registered in one place (`registry.py`) with their OpenAI schemas and Python function references. Adding a new tool means adding one entry.

6. **Streamlit for the UI**: Provides a chat interface with sidebar controls, tool execution tracing, and example prompts — all in pure Python with no frontend build step.

---

## ⚖️ Trade-offs and Limitations

| Decision | Trade-off |
|----------|-----------|
| Heuristic scoring vs. ML model | Explainable but less accurate. A production system would use trained models. |
| SQLite vs. PostgreSQL/real DB | Easy to run locally but doesn't demonstrate connection pooling or real DB ops. |
| Single agent vs. multi-agent | Simpler but all logic routes through one LLM context. Multi-agent could specialize. |
| OpenAI dependency | Requires API key and internet. Could swap for local LLM but quality would drop. |
| Synthetic data | Realistic patterns but not real-world distributions. Production would connect to actual CRM. |
| Message template + LLM | Messages have a template base enhanced by LLM. Fully LLM-generated messages could be more creative but less consistent. |
| No authentication | Demo system has no user auth. Production would need RBAC for RM access control. |

---

## 🚀 Setup and Run Instructions

### Prerequisites
- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Clone the repository
```bash
git clone https://github.com/parth4673
/banking-crm-agent.git
cd banking-crm-agent
```

### Step 2: Create a virtual environment
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure your API key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Or set it directly:
```bash
export OPENAI_API_KEY="sk-your-key-here"   # macOS/Linux
set OPENAI_API_KEY=sk-your-key-here        # Windows CMD
$env:OPENAI_API_KEY="sk-your-key-here"     # Windows PowerShell
```

### Step 5: Run the app
```bash
python main.py
```
This will seed the database and launch the Streamlit UI at `http://localhost:8501`.

### Alternative: CLI mode (no UI)
```bash
python main.py --cli
```

---

## 📂 Project Structure

```
banking-crm-agent/
├── main.py                  # Entry point — seeds DB, launches app
├── config.py                # Configuration (API keys, DB path)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore
│
├── agent/                   # 🧠 Agent orchestration
│   ├── __init__.py
│   ├── agent.py             # Core agent loop (LLM + tool execution)
│   └── prompts.py           # System prompt
│
├── tools/                   # 🔧 Tool implementations
│   ├── __init__.py
│   ├── customer_tools.py    # Customer queries (search, filter, profile)
│   ├── scoring_tools.py     # Conversion likelihood scoring
│   ├── product_tools.py     # Product recommendations
│   ├── message_tools.py     # WhatsApp message generation
│   └── registry.py          # Tool schemas + function map
│
├── database/                # 💾 Data layer
│   ├── __init__.py
│   ├── db.py                # SQLite connection + query helpers
│   └── seed.py              # Synthetic data generation
│
└── ui/                      # 🖥️ User interface
    └── app.py               # Streamlit chat application
```

---

## 🧪 Demo Use Cases

### Use Case 1: Full outreach pipeline
> "Find high-value customers likely to convert for a personal loan this month and generate personalized WhatsApp messages."

### Use Case 2: Targeted segment analysis
> "Show me Premium customers in Mumbai with credit score above 750 and recommend products."

### Use Case 3: Individual customer deep-dive
> "Give me the full profile of CUST0005, score them for a credit card, and generate an outreach message."

### Use Case 4: Occupation-based prospecting
> "Search for customers who are doctors, score them for home loans, and generate messages for the top 3."

### Use Case 5: Product-first exploration
> "What products can we offer to customer CUST0012? Draft WhatsApp messages for the top 2 recommendations."

---

## 📄 License

MIT
