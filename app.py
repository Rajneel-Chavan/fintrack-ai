# app.py — Production MCP Expense Tracker with LangChain + Streamlit

import os
import json
import asyncio
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import (
    HumanMessage, AIMessage, ToolMessage, SystemMessage
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinTrack AI",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;500;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Background */
.stApp {
    background: #0a0a0f;
}

/* Hide default header */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Main container */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 900px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e2e;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Title */
.fin-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}

.fin-subtitle {
    font-size: 0.8rem;
    color: #4ade80;
    font-family: 'Space Mono', monospace;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0d2818;
    border: 1px solid #4ade80;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.7rem;
    color: #4ade80;
    font-family: 'Space Mono', monospace;
    margin-bottom: 1rem;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #4ade80;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Chat messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* User message */
[data-testid="stChatMessageContent"] {
    background: #13131f !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
}

/* Tool call indicator */
.tool-call-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1a0d2e;
    border: 1px solid #7c3aed;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: #a78bfa;
    font-family: 'Space Mono', monospace;
    margin: 4px 2px;
}

/* Chat input */
.stChatInputContainer {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
}

.stChatInputContainer textarea {
    color: #e2e8f0 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.9rem !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px;
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.75rem !important;
    font-family: 'Space Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.4rem !important;
}

/* Divider */
hr {
    border-color: #1e1e2e !important;
}

/* Quick action buttons */
.stButton button {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-family: 'Sora', sans-serif !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-align: left !important;
    padding: 8px 12px !important;
}

.stButton button:hover {
    border-color: #4ade80 !important;
    color: #4ade80 !important;
    background: #0d2818 !important;
}

/* Sidebar text */
.sidebar-label {
    font-size: 0.68rem;
    color: #475569;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
    margin-top: 20px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e1e2e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2d2d40; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MCP SERVER CONFIG
# ─────────────────────────────────────────────
SERVERS = {
    "expense": {
        "transport": "streamable_http",
        "url": "https://pale-coffee-cougar.fastmcp.app/mcp"
    }
}

SYSTEM_PROMPT = """You are FinTrack AI, an intelligent personal finance assistant.
You have access to a full-featured expense tracking system with these capabilities:

EXPENSE MANAGEMENT:
- add_expense: Log expenses with date, amount, category, subcategory, note, payment_mode (cash/upi/card/netbanking)
- list_expenses: View expenses filtered by date range, category, payment mode
- update_expense: Modify any expense by ID
- delete_expense: Remove an expense by ID
- search_expenses: Search by keyword across notes and categories

ANALYTICS:
- summarize: Category-wise totals with stats for any period
- monthly_summary: Complete P&L — income, expenses, savings rate, top 5 expenses
- spending_trend: Month-by-month spending trend
- top_spending_categories: Ranked categories by spend
- daily_average: Average daily spending for any period
- net_worth_snapshot: Total income vs expenses for any period

INCOME:
- add_credit: Log income/salary/freelance
- list_credits: View all income entries

BUDGETS:
- set_budget: Set monthly spending limit per category
- check_budget: Compare actual vs budget with warning alerts

RECURRING:
- add_recurring: Set up recurring expenses (rent, subscriptions)
- list_recurring: View all recurring entries
- due_reminders: Check what's due today or overdue

Use today's date: """ + datetime.now().strftime("%Y-%m-%d") + """

Be concise. Show amounts in ₹. Format summaries as clean structured responses."""

# ─────────────────────────────────────────────
# QUICK ACTIONS
# ─────────────────────────────────────────────
QUICK_ACTIONS = [
    ("📊 Monthly summary", f"Give me a complete summary for {datetime.now().strftime('%B %Y')}"),
    ("💰 Check budgets", f"How am I doing against my budgets this month?"),
    ("📈 Spending trend", "Show my spending trend for the last 6 months"),
    ("⚠️ Due reminders", "What recurring bills are due today or overdue?"),
    ("🏆 Top categories", "What are my top 5 spending categories this month?"),
    ("📅 Daily average", f"What's my daily average spend this month?"),
]

# ─────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────
load_dotenv()

if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ─────────────────────────────────────────────
# INITIALIZE SESSION STATE
# ─────────────────────────────────────────────
if "initialized" not in st.session_state:
    with st.spinner("Connecting to FinTrack AI..."):
        try:
            st.session_state.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0
            )
            st.session_state.client = MultiServerMCPClient(SERVERS)
            tools = asyncio.run(st.session_state.client.get_tools())
            st.session_state.tools = tools
            st.session_state.tool_by_name = {t.name: t for t in tools}
            st.session_state.llm_with_tools = st.session_state.llm.bind_tools(tools)
            st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
            st.session_state.tool_calls_made = []
            st.session_state.initialized = True
            st.session_state.connected = True
            st.session_state.tool_count = len(tools)
        except Exception as e:
            st.session_state.connected = False
            st.session_state.error = str(e)
            st.session_state.initialized = True

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="fin-title">💸 FinTrack</div>', unsafe_allow_html=True)
    st.markdown('<div class="fin-subtitle">AI Finance Assistant</div>', unsafe_allow_html=True)

    if st.session_state.get("connected"):
        st.markdown(
            f'<div class="status-badge"><div class="status-dot"></div>'
            f'MCP CONNECTED · {st.session_state.tool_count} TOOLS</div>',
            unsafe_allow_html=True
        )
    else:
        st.error("MCP Connection Failed")
        if st.session_state.get("error"):
            st.caption(st.session_state.error)

    st.markdown('<div class="sidebar-label">Quick Actions</div>', unsafe_allow_html=True)

    for label, prompt in QUICK_ACTIONS:
        if st.button(label, key=f"qa_{label}"):
            st.session_state.quick_action = prompt

    st.markdown('<div class="sidebar-label">Example Commands</div>', unsafe_allow_html=True)
    examples = [
        '💳 "Add ₹450 UPI for groceries today"',
        '💼 "Log ₹50000 salary received today"',
        '🎯 "Set food budget to ₹8000"',
        '🔄 "Add ₹999 Netflix monthly subscription"',
        '🔍 "Search expenses for Swiggy"',
    ]
    for ex in examples:
        st.caption(ex)

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Session</div>', unsafe_allow_html=True)
    msg_count = len([m for m in st.session_state.get("history", [])
                     if isinstance(m, (HumanMessage, AIMessage))])
    st.caption(f"Messages: {msg_count}")
    st.caption(f"Date: {datetime.now().strftime('%d %b %Y')}")

    if st.button("🗑️ Clear Chat", key="clear"):
        st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.tool_calls_made = []
        st.rerun()

# ─────────────────────────────────────────────
# MAIN CHAT AREA
# ─────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="fin-title">FinTrack AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fin-subtitle">Personal Finance · Powered by MCP + LangChain</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# Render chat history
for msg in st.session_state.get("history", []):
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        if getattr(msg, "tool_calls", None):
            continue
        if msg.content:
            with st.chat_message("assistant", avatar="💸"):
                st.markdown(msg.content)

# Handle quick action
user_text = None
if "quick_action" in st.session_state:
    user_text = st.session_state.pop("quick_action")

# Handle chat input
chat_input = st.chat_input("Ask about your finances... e.g. 'Add ₹500 for lunch today'")
if chat_input:
    user_text = chat_input

# Process message
if user_text and st.session_state.get("connected"):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)
    st.session_state.history.append(HumanMessage(content=user_text))

    with st.chat_message("assistant", avatar="💸"):
        with st.spinner("Thinking..."):
            try:
                # First pass — decide tools or direct answer
                first = asyncio.run(
                    st.session_state.llm_with_tools.ainvoke(
                        st.session_state.history
                    )
                )
                tool_calls = getattr(first, "tool_calls", None)

                if not tool_calls:
                    st.markdown(first.content or "")
                    st.session_state.history.append(first)
                else:
                    # Show tool usage
                    tool_names = [tc["name"] for tc in tool_calls]
                    badges = " ".join([
                        f'<span class="tool-call-badge">⚡ {n}</span>'
                        for n in tool_names
                    ])
                    st.markdown(
                        f'<div style="margin-bottom:8px">{badges}</div>',
                        unsafe_allow_html=True
                    )

                    # Append assistant with tool calls
                    st.session_state.history.append(first)

                    # Execute tools
                    tool_msgs = []
                    for tc in tool_calls:
                        name = tc["name"]
                        args = tc.get("args") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                pass
                        tool = st.session_state.tool_by_name[name]
                        res = asyncio.run(tool.ainvoke(args))
                        tool_msgs.append(
                            ToolMessage(
                                tool_call_id=tc["id"],
                                content=json.dumps(res)
                            )
                        )
                        st.session_state.tool_calls_made.append(name)

                    st.session_state.history.extend(tool_msgs)

                    # Final reply
                    final = asyncio.run(
                        st.session_state.llm.ainvoke(
                            st.session_state.history
                        )
                    )
                    st.markdown(final.content or "")
                    st.session_state.history.append(
                        AIMessage(content=final.content or "")
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")

elif user_text and not st.session_state.get("connected"):
    st.error("MCP server not connected. Check your server path.")