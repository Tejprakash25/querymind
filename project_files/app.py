"""
app.py — QueryMind: Talk to Your Database in Plain English
Run: streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
from seed_db import seed as _seed, DB_PATH as _DB_PATH
from db_engine import get_schema, get_schema_detailed, execute_query, db_exists
from llm_engine import generate_sql, get_provider_info

# ---------------------------------------------------------------------------
# Auto-seed database if not found (handles Streamlit Cloud cold starts)
# ---------------------------------------------------------------------------
if not db_exists():
    _seed(silent=True)

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="QueryMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .qm-header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid #21262d;
        margin-bottom: 1.5rem;
    }
    .qm-title {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4aa;
        margin: 0;
    }
    .qm-subtitle {
        color: #8b8fa8;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    .qm-badge {
        display: inline-block;
        background: #1a1d27;
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.78rem;
        color: #8b8fa8;
        margin-top: 0.5rem;
    }
    .stButton > button {
        background-color: #1a1d27 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        padding: 0.4rem 0.6rem !important;
        width: 100%;
        text-align: left !important;
        transition: border-color 0.2s;
    }
    .stButton > button:hover {
        border-color: #00d4aa !important;
        color: #00d4aa !important;
    }
    .qm-label {
        font-size: 0.8rem;
        color: #8b8fa8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
        margin-top: 1rem;
    }
    .qm-result-meta {
        font-size: 0.85rem;
        color: #8b8fa8;
        margin-bottom: 0.5rem;
    }
    .qm-error {
        background: #2d1b1b;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 1rem;
        color: #fca5a5;
        font-size: 0.9rem;
    }
    .stTextInput > div > div > input {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 1px #00d4aa !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
provider = get_provider_info()
st.markdown(f"""
<div class="qm-header">
    <p class="qm-title">🧠 QueryMind</p>
    <p class="qm-subtitle">Talk to your database in plain English — no SQL required.</p>
    <span class="qm-badge">⚡ {provider['provider']} · {provider['model']}</span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Layout: two columns
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1, 2], gap="large")

# ---------------------------------------------------------------------------
# LEFT COLUMN — Schema viewer + examples
# ---------------------------------------------------------------------------
with col_left:
    st.markdown("#### 📊 Database Schema")
    with st.expander("View Tables", expanded=True):
        st.code(get_schema_detailed(), language="sql")

    st.markdown("#### 💡 Try These Questions")
    examples = [
        "Show top 5 customers by total orders",
        "Which products are out of stock?",
        "Total revenue by product category",
        "List all pending orders",
        "Which city has the most customers?",
        "Show orders placed in the last 30 days",
        "Average order amount per customer",
        "Top 3 most expensive products",
    ]

    if "question_input" not in st.session_state:
        st.session_state["question_input"] = ""

    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state["question_input"] = ex
            st.rerun()

# ---------------------------------------------------------------------------
# RIGHT COLUMN — Query input + results
# ---------------------------------------------------------------------------
with col_right:
    st.markdown("#### 💬 Ask Your Question")

    question = st.text_input(
        label="question",
        label_visibility="collapsed",
        value=st.session_state.get("question_input", ""),
        placeholder="e.g. Show me top 5 products by total sales amount",
        key="main_input",
    )

    run_btn = st.button("🔍 Generate & Run Query", type="primary", use_container_width=True)

    if run_btn and question.strip():
        schema = get_schema()
        sql = ""
        df = None
        error_msg = ""

        with st.spinner("Generating SQL..."):
            try:
                sql = generate_sql(schema, question)
            except RuntimeError as e:
                st.markdown(
                    f'<div class="qm-error">❌ LLM Error: {str(e)}</div>',
                    unsafe_allow_html=True
                )
                st.stop()

        if sql:
            with st.spinner("Running query..."):
                try:
                    df = execute_query(sql)
                except ValueError as e:
                    error_msg = str(e)
                    # Retry with error feedback
                    try:
                        sql = generate_sql(schema, question, error_feedback=error_msg)
                        df = execute_query(sql)
                        error_msg = ""
                    except (ValueError, RuntimeError) as e2:
                        error_msg = str(e2)

            st.markdown('<p class="qm-label">Generated SQL</p>', unsafe_allow_html=True)
            st.code(sql, language="sql")

            if df is not None and error_msg == "":
                row_count = len(df)
                st.markdown(
                    f'<p class="qm-result-meta">✅ {row_count} row{"s" if row_count != 1 else ""} returned</p>',
                    unsafe_allow_html=True
                )
                if row_count == 0:
                    st.info("Query ran successfully but returned no rows.")
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=df.to_csv(index=False).encode("utf-8"),
                        file_name="querymind_results.csv",
                        mime="text/csv",
                    )
            else:
                st.markdown(
                    f'<div class="qm-error">❌ Could not execute query.<br><br>'
                    f'<strong>Error:</strong> {error_msg}<br><br>'
                    f'Try rephrasing your question.</div>',
                    unsafe_allow_html=True
                )

    elif run_btn and not question.strip():
        st.warning("Please enter a question before running.")

    if not run_btn:
        st.markdown("""
        <div style="margin-top:2rem; padding:1.5rem; background:#161b22;
                    border:1px dashed #30363d; border-radius:10px; color:#8b8fa8;
                    text-align:center;">
            ← Pick an example question or type your own above.<br>
            <span style="font-size:0.8rem;">
                QueryMind converts plain English → SQL → live results.
            </span>
        </div>
        """, unsafe_allow_html=True)