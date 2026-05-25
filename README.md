# FinTrack AI 💸

> An intelligent personal finance assistant powered by **MCP (Model Context Protocol)** + **LangChain** + **Streamlit**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-FinTrack%20AI-green?style=for-the-badge)](https://fintrack-ai-2waa.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-orange?style=for-the-badge)](https://langchain.com)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-purple?style=for-the-badge)](https://fastmcp.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=for-the-badge)](https://streamlit.io)

---

## 🎯 Overview

FinTrack AI is a production-grade personal finance assistant that lets you manage your finances through **natural language conversations**. Instead of filling forms or clicking through dashboards, simply type what you want:

> *"Add ₹450 UPI payment for groceries today"*  
> *"Give me my complete May 2026 summary"*  
> *"Am I over budget this month?"*

Built on **Model Context Protocol (MCP)** — the emerging standard for connecting AI models to external tools and data sources — FinTrack AI demonstrates how LLMs can interact with persistent databases to perform real-world actions, not just generate text.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Interface                  │
│         Streamlit Chat (Dark Theme UI)           │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              LangChain Agent Layer               │
│   ChatOpenAI (gpt-4o-mini) + Tool Binding        │
│   Message History + Tool Call Orchestration      │
└──────────────────────┬──────────────────────────┘
                       │  MCP Protocol
                       ▼
┌─────────────────────────────────────────────────┐
│           MCP Server (FastMCP)                   │
│         18 Tools + 2 Live Resources              │
│    STDIO Transport (local) / HTTP (remote)       │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              SQLite Database                     │
│   4 Tables: expenses, credits, budgets,          │
│             recurring                            │
└─────────────────────────────────────────────────┘
```

---

## ✨ Features

### 💳 Expense Management
- Add expenses with payment mode tracking (cash / UPI / card / netbanking)
- List, filter, update, and delete expenses by date range or category
- Keyword search across all expense notes and categories

### 📊 Analytics & Insights
- **Monthly P&L Report** — total income, expenses, net savings, savings rate
- **Spending Trend** — month-by-month breakdown for last N months
- **Top Categories** — ranked spending categories by total amount
- **Daily Average** — average spend per day for any period
- **Net Worth Snapshot** — income vs expenses for any date range

### 💰 Income Tracking
- Log salary, freelance income, and other credits
- View income history by date range

### 🎯 Budget Management
- Set monthly spending limits per category
- Real-time budget vs actual comparison
- Visual status: ✅ OK / ⚠️ Warning (>80%) / ❌ Over Budget

### 🔄 Recurring Expenses
- Track subscriptions, rent, EMIs with frequency (daily/weekly/monthly/yearly)
- Due reminders for overdue or today's recurring bills

### 📡 Live MCP Resources
- `expense:///summary/today` — real-time today's spending snapshot
- `expense:///categories` — live category configuration

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (custom dark theme, Space Mono + Sora fonts) |
| **LLM** | OpenAI GPT-4o-mini via LangChain |
| **Agent Framework** | LangChain MCP Adapters |
| **MCP Server** | FastMCP (Python) |
| **Database** | SQLite with WAL mode (async via aiosqlite) |
| **Deployment** | Render (app) + FastMCP Cloud (MCP server) |
| **Protocol** | MCP — STDIO (local) / Streamable HTTP (remote) |

---

## 📋 MCP Tools (18 Total)

### Expense Tools
| Tool | Description |
|---|---|
| `add_expense` | Log expense with date, amount, category, payment mode |
| `list_expenses` | Filter expenses by date, category, payment mode |
| `update_expense` | Modify any field of existing expense by ID |
| `delete_expense` | Remove expense by ID |
| `search_expenses` | Keyword search across notes and categories |

### Analytics Tools
| Tool | Description |
|---|---|
| `summarize` | Category totals with count, avg, min, max |
| `monthly_summary` | Complete P&L with savings rate and top 5 expenses |
| `spending_trend` | Month-by-month trend for last N months |
| `top_spending_categories` | Ranked top N categories by spend |
| `daily_average` | Average daily spending for any period |
| `net_worth_snapshot` | Income vs expenses net position |

### Income Tools
| Tool | Description |
|---|---|
| `add_credit` | Log income or credit entry |
| `list_credits` | View income entries by date range |

### Budget Tools
| Tool | Description |
|---|---|
| `set_budget` | Set monthly limit per category |
| `check_budget` | Budget vs actual with status warnings |

### Recurring Tools
| Tool | Description |
|---|---|
| `add_recurring` | Add recurring expense with frequency |
| `list_recurring` | View all active recurring entries |
| `due_reminders` | Get overdue or today's due bills |

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.10+
OpenAI API Key
```

### Installation

```bash
# Clone the repository
git clone https://github.com/rajneelchavan/fintrack-ai.git
cd fintrack-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Run Locally

```bash
streamlit run app.py
```

The app connects to the MCP server (`server.py`) automatically via STDIO transport.

---

## 🌐 Deployment

### App — Render
```
https://fintrack-ai-2waa.onrender.com/
```

### MCP Server — FastMCP Cloud
```
https://pale-coffee-cougar.fastmcp.app/mcp
```

### Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ExpenseTracker": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://pale-coffee-cougar.fastmcp.app/mcp"
      ]
    }
  }
}
```

---

## 💬 Example Conversations

```
User: Add ₹450 UPI payment for groceries today
AI:   ✅ Added ₹450 for Food & Dining (UPI) on 2026-05-25

User: Give me my complete May 2026 summary
AI:   📊 May 2026 Summary
      Income:   ₹50,000
      Expenses: ₹32,450
      Savings:  ₹17,550 (35.1%)
      Top spend: Food ₹8,200 | Transport ₹4,500

User: Am I over budget anywhere this month?
AI:   ⚠️  Food & Dining: ₹8,200/₹8,000 — OVER BUDGET
      ✅  Transport: ₹4,500/₹6,000 — 75% used
      ✅  Entertainment: ₹1,200/₹3,000 — 40% used

User: What bills are due today?
AI:   🔔 Netflix ₹999 — due today (monthly)
      🔔 Gym membership ₹1,500 — overdue since May 20
```

---

## 📁 Project Structure

```
fintrack-ai/
├── app.py              # Streamlit frontend + LangChain agent
├── server.py           # FastMCP server with 18 tools
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── secrets.toml    # API keys (not in repo)
├── .gitignore
└── README.md
```

---

## 🔑 Key Technical Decisions

**Why MCP over direct function calling?**  
MCP provides a standardized protocol for LLM-tool communication. The same server works with Claude Desktop, Cursor, Windsurf, and any MCP-compatible client without code changes.

**Why async SQLite (aiosqlite)?**  
Prevents blocking the event loop during database operations, enabling better performance under concurrent requests in the production deployment.

**Why SQLite over PostgreSQL?**  
For a personal finance tool, SQLite provides zero-infrastructure persistence with ACID compliance. WAL mode enables concurrent reads without locking.

**Why STDIO + HTTP dual transport?**  
STDIO for local Claude Desktop integration (fast, zero network overhead). HTTP for cloud deployment (accessible from anywhere, supports OAuth authentication).

---

## 🤝 Connect

**Rajneel Chavan**  
- GitHub: [@rajneelchavan](https://github.com/rajneelchavan)  
- LinkedIn: [linkedin.com/in/rajneelchavan](https://linkedin.com/in/rajneelchavan)  
- Email: rajneelchavan16@gmail.com

---

## 📄 License

MIT License — feel free to use this project as a reference for your own MCP-powered applications.

---

*Built with ❤️ as part of an AI Engineering learning journey — exploring production-grade Agentic AI systems with LangChain, MCP, and LangGraph.*
