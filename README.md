# 🧠 QueryMind — Talk to Your Database in Plain English

> **An AI-powered Text-to-SQL web app that converts natural language questions into real SQL queries and returns live results — no SQL knowledge required.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?logo=ollama)](https://ollama.ai)
[![Groq](https://img.shields.io/badge/Groq-Free_API-orange)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Deploy on Streamlit](https://img.shields.io/badge/Deploy-Streamlit_Cloud-ff4b4b)](https://streamlit.io/cloud)

---

## 📌 Table of Contents

- [Product Requirements Document (PRD)](#-product-requirements-document-prd)
- [App Flow](#-app-flow)
- [Tech Stack](#-tech-stack)
- [Frontend Guidelines](#-frontend-guidelines)
- [Backend & Database Schema](#-backend--database-schema)
- [Implementation Guide](#-implementation-guide)
- [Project Structure](#-project-structure)
- [Environment Setup](#-environment-setup)
- [Running Locally](#-running-locally)
- [Free Deployment (Streamlit Cloud)](#-free-deployment-streamlit-cloud)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)

---

## 📋 Product Requirements Document (PRD)

### Problem Statement
Non-technical users (analysts, managers, students) need to query databases but don't know SQL. Writing SQL manually is slow, error-prone, and a blocker for data access.

### Solution
QueryMind lets users ask plain English questions like *"How many orders were placed last month?"* and instantly returns the SQL query + live results — powered by a local or free LLM.

### Target Users
- Computer engineering students building AI portfolio projects
- Non-technical users who need data insights
- Developers prototyping AI-integrated data tools

### Goals
| Goal | Metric |
|------|--------|
| Convert natural language to valid SQL | >85% query accuracy on test cases |
| Return results within 5 seconds | Response time < 5s on local LLM |
| Zero cost to run and deploy | $0 infra cost using free tier tools |
| Clean, usable UI | Single-page Streamlit app |

### Non-Goals (v1)
- No user authentication
- No multi-database support (PostgreSQL, MySQL) in v1
- No query history persistence across sessions
- No paid API usage

### Success Criteria
- App runs fully locally with Ollama OR on cloud via Groq free API
- Deployed live on Streamlit Cloud with a shareable URL
- README + demo GIF ready for GitHub portfolio

---

## 🔄 App Flow

```
User opens app
     │
     ▼
[Streamlit UI loads]
     │
     ├── Shows: Database schema (table names + columns)
     ├── Shows: Example questions user can ask
     └── Shows: Text input box
            │
            ▼
     User types question in plain English
     e.g. "Show top 5 products by total sales"
            │
            ▼
     [Python Backend]
            │
            ├── Fetches DB schema dynamically from SQLite
            ├── Builds prompt:
            │     "Given this schema: {schema}
            │      Convert this question to SQL: {question}
            │      Return only valid SQL, nothing else."
            │
            ▼
     [LLM Layer — Gemma 27B via Ollama OR Llama3 via Groq]
            │
            ▼
     LLM returns SQL query
     e.g. SELECT product_name, SUM(amount) FROM orders
          GROUP BY product_name ORDER BY SUM(amount) DESC LIMIT 5
            │
            ▼
     [Validation Layer]
            ├── Is it valid SQL syntax? → Yes: proceed
            └── No: retry prompt with error feedback (max 2 retries)
            │
            ▼
     Execute SQL on SQLite database
            │
            ├── Success → Return results as DataFrame
            └── Error   → Show user-friendly error message
            │
            ▼
     [Streamlit UI]
            ├── Shows: Generated SQL (syntax highlighted)
            ├── Shows: Result table
            └── Shows: Download as CSV button
```

---

## 🛠 Tech Stack

### Core (All Free, All Local or Free-Tier Cloud)

| Layer | Tool | Why |
|-------|------|-----|
| **UI** | Streamlit | Fastest Python UI, free cloud hosting |
| **LLM (local dev)** | Ollama + Gemma 27B | Runs on your PC, zero API cost |
| **LLM (deployed)** | Groq API (free tier) | Fast inference, free, works on Streamlit Cloud |
| **Database** | SQLite | Zero setup, file-based, ships with Python |
| **LLM Bridge** | LangChain | Prompt chaining, easy LLM switching |
| **Data display** | Pandas | DataFrame rendering in Streamlit |
| **Deployment** | Streamlit Cloud | Free, GitHub-connected, 1-click deploy |

### Python Libraries
```txt
streamlit>=1.32.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-groq>=0.1.0
pandas>=2.0.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
```

### Why Groq for Deployment (Not Ollama)?
Streamlit Cloud is a server — it can't run Ollama. Groq offers **free API access** to Llama 3 and Gemma models with generous rate limits. The switch is one line of code.

---

## 🎨 Frontend Guidelines

### Design Philosophy
Clean, dark, developer-aesthetic. Think "terminal meets dashboard." No clutter.

### Color Palette
```css
--bg-primary:     #0e1117   /* Streamlit dark default */
--bg-secondary:   #1a1d27   /* Card/panel backgrounds */
--accent:         #00d4aa   /* Teal — action elements */
--text-primary:   #fafafa
--text-muted:     #8b8fa8
--success:        #21c55d
--error:          #ef4444
--code-bg:        #161b22   /* SQL code block */
```

### Layout Rules
- **Single page** — no tabs, no sidebar complexity in v1
- **3-section layout:** Schema viewer (left column) | Main input+output (right column)
- **SQL output** always shown in a styled code block (use `st.code(sql, language="sql")`)
- **Results table** below SQL — clean, no index column
- **Mobile-friendly** — Streamlit handles this by default

### UI Components (Streamlit)
```python
# Main input
question = st.text_input("💬 Ask your database anything...",
    placeholder="e.g. Show me top 5 customers by total orders")

# SQL display
st.code(generated_sql, language="sql")

# Results
st.dataframe(result_df, use_container_width=True, hide_index=True)

# Download
st.download_button("⬇️ Download CSV", result_df.to_csv(), "results.csv")
```

### What NOT to do
- No excessive emojis
- No loading spinners that hang (add timeout handling)
- No raw error tracebacks shown to user — catch and show friendly messages

---

## 🗄 Backend & Database Schema

### Sample Database: E-Commerce Store (`querymind.db`)

Built with SQLite. Seeded automatically on first run via `seed_db.py`.

#### Table: `customers`
```sql
CREATE TABLE customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    city        TEXT,
    created_at  DATE DEFAULT CURRENT_DATE
);
```

#### Table: `products`
```sql
CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL,
    stock       INTEGER DEFAULT 0
);
```

#### Table: `orders`
```sql
CREATE TABLE orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER REFERENCES customers(id),
    product_id   INTEGER REFERENCES products(id),
    quantity     INTEGER NOT NULL,
    amount       REAL NOT NULL,
    order_date   DATE DEFAULT CURRENT_DATE,
    status       TEXT DEFAULT 'pending'
);
```

### Schema Fetching (Dynamic — works with any SQLite DB)
```python
def get_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    schema = []
    for (table,) in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_str = ", ".join([f"{c[1]} ({c[2]})" for c in cols])
        schema.append(f"Table: {table} | Columns: {col_str}")
    conn.close()
    return "\n".join(schema)
```

---

## ⚙️ Implementation Guide

### Step 1 — Project Setup
```bash
git clone https://github.com/YOUR_USERNAME/querymind
cd querymind
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Seed the Database
```bash
python seed_db.py
# Creates querymind.db with sample customers, products, orders
```

### Step 3 — Configure Environment
Create a `.env` file:
```env
# For local development (Ollama)
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma:27b

# For deployment (Groq - free)
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_free_key_from_groq.com
# GROQ_MODEL=llama3-70b-8192
```

### Step 4 — Core LLM Logic (`llm_engine.py`)
```python
from langchain_community.llms import Ollama
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "groq":
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL", "llama3-70b-8192")
        )
    return Ollama(model=os.getenv("OLLAMA_MODEL", "gemma:27b"))

SQL_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template="""You are an expert SQL assistant.
Given this database schema:
{schema}

Convert the following question into a valid SQLite SQL query.
Return ONLY the SQL query. No explanation. No markdown. No backticks.

Question: {question}
SQL:"""
)

def generate_sql(schema: str, question: str) -> str:
    llm = get_llm()
    chain = SQL_PROMPT | llm
    result = chain.invoke({"schema": schema, "question": question})
    # Handle both string and AIMessage responses
    return result.content if hasattr(result, "content") else str(result)
```

### Step 5 — SQL Execution with Retry (`db_engine.py`)
```python
import sqlite3
import pandas as pd

def execute_sql(query: str, db_path: str = "querymind.db") -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise ValueError(f"SQL execution failed: {str(e)}")
    finally:
        conn.close()
```

### Step 6 — Streamlit App (`app.py`)
```python
import streamlit as st
from llm_engine import generate_sql
from db_engine import execute_sql, get_schema
import sqlite3

st.set_page_config(page_title="QueryMind", page_icon="🧠", layout="wide")
st.title("🧠 QueryMind")
st.caption("Ask your database anything in plain English.")

# Schema viewer
with st.expander("📊 View Database Schema", expanded=False):
    st.code(get_schema("querymind.db"), language="sql")

# Example questions
st.markdown("**Try asking:**")
examples = [
    "Show top 5 customers by total orders",
    "Which products are out of stock?",
    "Total revenue by product category",
    "Orders placed this month"
]
cols = st.columns(4)
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True):
        st.session_state["question"] = ex

# Input
question = st.text_input("💬 Your question:", 
    value=st.session_state.get("question", ""),
    placeholder="e.g. Show me all orders above 500 rupees")

if st.button("🔍 Generate & Run", type="primary") and question:
    with st.spinner("Thinking..."):
        schema = get_schema("querymind.db")
        
        # Retry logic
        for attempt in range(2):
            try:
                sql = generate_sql(schema, question)
                sql = sql.strip().strip("`").replace("```sql", "").replace("```", "")
                
                st.markdown("### Generated SQL")
                st.code(sql, language="sql")
                
                df = execute_sql(sql)
                st.markdown(f"### Results — {len(df)} rows")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Download CSV", df.to_csv(index=False), "results.csv")
                break
            except Exception as e:
                if attempt == 1:
                    st.error(f"Could not generate a valid query. Try rephrasing your question.")
```

### Step 7 — Run It
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

---

## 📁 Project Structure

```
querymind/
│
├── app.py                  # Main Streamlit application
├── llm_engine.py           # LLM integration (Ollama + Groq)
├── db_engine.py            # SQLite query execution
├── seed_db.py              # Database seeder (run once)
│
├── querymind.db            # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
├── .env                    # API keys (never commit this)
├── .env.example            # Template for env vars
├── .gitignore
│
├── README.md
└── assets/
    └── demo.gif            # Screen recording for README
```

---

## 🔧 Environment Setup

### Option A — Local Dev with Ollama
```bash
# Install Ollama from https://ollama.ai
ollama pull gemma:27b        # or: ollama pull llama3

# Set in .env:
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma:27b
```

### Option B — Deployed with Groq (Free)
1. Go to [console.groq.com](https://console.groq.com) → create free account → get API key
2. Set in `.env`:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL=llama3-70b-8192
```

---

## 🚀 Free Deployment (Streamlit Cloud)

**Cost: ₹0. Forever.**

1. Push code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set secrets in Streamlit Cloud dashboard:
   ```
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "your_key"
   GROQ_MODEL = "llama3-70b-8192"
   ```
5. Click Deploy → get public URL like `querymind.streamlit.app`

> **Note:** Switch to Groq for deployment — Streamlit Cloud can't run Ollama locally.

---

## 🔮 Future Improvements

- [ ] Upload your own SQLite / CSV file and query it
- [ ] Support PostgreSQL and MySQL connections
- [ ] Query history with session memory
- [ ] Natural language explanation of results
- [ ] Multi-step agentic queries ("First filter, then summarize")
- [ ] Voice input support
- [ ] Export results to Excel

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

## 📄 License

MIT License — use freely, credit appreciated.

---

> Built with 🧠 using Ollama, Groq, LangChain, and Streamlit — fully free stack.
