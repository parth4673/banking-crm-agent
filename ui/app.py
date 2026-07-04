"""
Streamlit Chat UI for the Banking CRM Agent.

Provides a conversational interface for Relationship Managers.
Shows real-time tool execution status and expandable traces.
"""

import streamlit as st
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.seed import seed_database
from agent.agent import BankingCRMAgent
from config import OPENAI_API_KEY

# Page config
st.set_page_config(
    page_title="Banking CRM Agent",
    page_icon="🏦",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .tool-call-box {
        background-color: #f0f2f6;
        border-left: 4px solid #4A90D9;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.85em;
    }
    .tool-call-box.error {
        border-left-color: #d32f2f;
    }
    .tool-name {
        color: #4A90D9;
        font-weight: 700;
        font-size: 0.95em;
    }
    .step-badge {
        background-color: #4A90D9;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        margin-right: 8px;
    }
    .status-badge-success {
        background-color: #4CAF50;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7em;
    }
    .status-badge-error {
        background-color: #d32f2f;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7em;
    }
</style>
""", unsafe_allow_html=True)

# Seed database
seed_database()

# Sidebar
with st.sidebar:
    st.title("🏦 Banking CRM Agent")
    st.markdown("---")

    api_key = st.text_input(
        "Groq API Key",
        value=OPENAI_API_KEY,
        type="password",
        help="Enter your Groq API key from console.groq.com",
    )

    model = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct"],
        index=0,
    )

    st.markdown("---")
    st.subheader("💡 Try these prompts")

    example_prompts = [
        "Find high-value customers likely to convert for a personal loan this month and generate personalized WhatsApp messages.",
        "Show me Premium segment customers in Mumbai with credit score above 750.",
        "Recommend products for customer CUST0005 and draft a WhatsApp message.",
        "Who are the top 5 customers most likely to take a credit card? Generate outreach for the best candidate.",
        "Search for customers who are doctors and score them for a home loan.",
    ]

    for prompt in example_prompts:
        if st.button(prompt, key=f"btn_{hash(prompt)}", use_container_width=True):
            st.session_state["pending_prompt"] = prompt

    st.markdown("---")
    st.subheader("📊 Database Stats")
    try:
        from database.db import run_query
        stats = run_query("SELECT COUNT(*) as count FROM customers WHERE is_active = 1")
        st.metric("Active Customers", stats[0]["count"])
        stats = run_query("SELECT COUNT(*) as count FROM transactions")
        st.metric("Transactions", stats[0]["count"])
        stats = run_query("SELECT COUNT(*) as count FROM products")
        st.metric("Products", stats[0]["count"])
    except Exception:
        st.info("Database loading...")

    st.markdown("---")
    st.markdown("**Supports:** OpenAI · Gemini · Groq")
    st.markdown("Change `base_url` in `agent.py` to switch providers.")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["agent"] = None
        st.rerun()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "agent" not in st.session_state:
    st.session_state["agent"] = None


def get_agent():
    if st.session_state["agent"] is None or api_key != getattr(st.session_state["agent"], "api_key", ""):
        if not api_key:
            return None
        st.session_state["agent"] = BankingCRMAgent(api_key=api_key, model=model)
    return st.session_state["agent"]


def render_tool_calls(tool_calls: list):
    if not tool_calls:
        return

    success_count = sum(1 for tc in tool_calls if tc.get("status") == "success")
    error_count = sum(1 for tc in tool_calls if tc.get("status") == "error")

    summary = f"🔧 Agent used {len(tool_calls)} tool(s)"
    if error_count > 0:
        summary += f" ({success_count} succeeded, {error_count} had errors)"

    with st.expander(summary, expanded=False):
        for tc in tool_calls:
            step = tc.get("step", "?")
            tool = tc.get("tool", "unknown")
            inputs = tc.get("input", {})
            output_preview = tc.get("output_preview", "")
            status = tc.get("status", "success")
            error = tc.get("error", "")

            status_badge = (
                '<span class="status-badge-success">✓ success</span>'
                if status == "success"
                else f'<span class="status-badge-error">✗ error</span>'
            )
            box_class = "tool-call-box error" if status == "error" else "tool-call-box"

            error_html = f"<br/><strong>Error:</strong> <code>{error}</code>" if error else ""

            st.markdown(f"""
<div class="{box_class}">
    <span class="step-badge">Step {step}</span>
    <span class="tool-name">🔧 {tool}</span> {status_badge}<br/>
    <strong>Input:</strong> <code>{json.dumps(inputs)}</code>
    {error_html}<br/>
    <strong>Output preview:</strong> <code>{output_preview[:300]}...</code>
</div>
""", unsafe_allow_html=True)


# Main chat area
st.title("🏦 Banking CRM Agent")
st.caption("AI-powered assistant for Relationship Managers • Ask about customers, products, scoring, and outreach")

# Display existing messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "tool_calls" in msg:
            render_tool_calls(msg["tool_calls"])
        st.markdown(msg["content"])

# Handle pending prompt from sidebar
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
else:
    prompt = st.chat_input("Ask me about customers, products, or outreach...")

# Process user input
if prompt:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    agent = get_agent()
    if agent is None:
        st.error("Could not initialize agent. Please check your API key.")
        st.stop()

    with st.chat_message("assistant"):
        status_placeholder = st.empty()

        def update_status(text):
            status_placeholder.markdown(f"*{text}*")

        try:
            result = agent.run(prompt, status_callback=update_status)

            # Clear the status
            status_placeholder.empty()

            # Show tool execution trace
            if result["tool_calls"]:
                render_tool_calls(result["tool_calls"])

            # Show response
            st.markdown(result["response"])

            st.session_state["messages"].append({
                "role": "assistant",
                "content": result["response"],
                "tool_calls": result["tool_calls"],
            })

        except Exception as e:
            status_placeholder.empty()
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state["messages"].append({
                "role": "assistant",
                "content": error_msg,
            })
