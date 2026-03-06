"""
llm_engine.py — LLM integration layer
Supports:
  - Ollama (local, for development)
  - Groq  (free API, for deployment on Streamlit Cloud)

Switch via LLM_PROVIDER env variable: "ollama" or "groq"
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER  = os.getenv("LLM_PROVIDER", "groq").lower()
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "gemma:2b")
OLLAMA_BASE   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama3-70b-8192")


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

def build_prompt(schema: str, question: str, error_feedback: str = "") -> str:
    error_section = ""
    if error_feedback:
        error_section = f"""
The previous SQL attempt failed with this error:
{error_feedback}
Please fix the query and try again.
"""
    return f"""You are an expert SQLite SQL assistant.

Database schema:
{schema}

Rules:
- Return ONLY a valid SQLite SELECT statement.
- Do NOT include markdown, backticks, code fences, or any explanation.
- Do NOT use MySQL or PostgreSQL syntax (no LIMIT after OFFSET, no backtick identifiers).
- Use double quotes for identifiers if needed, or no quotes for simple names.
- Always end the query with a semicolon.
{error_section}
Question: {question}
SQL:"""


# ---------------------------------------------------------------------------
# SQL cleanup — strips any markdown the LLM sneaks in anyway
# ---------------------------------------------------------------------------

def clean_sql(raw: str) -> str:
    """Remove markdown fences, leading/trailing whitespace, extra text."""
    # Remove ```sql ... ``` or ``` ... ```
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("`", "")
    # Keep only the first statement (up to and including first semicolon)
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip lines that look like prose / explanation
        if stripped.lower().startswith(("here", "the query", "this query",
                                         "note", "explanation", "answer")):
            continue
        lines.append(stripped)
    sql = " ".join(lines).strip()
    # Truncate after first semicolon
    if ";" in sql:
        sql = sql[: sql.index(";") + 1]
    return sql.strip()


# ---------------------------------------------------------------------------
# Ollama backend
# ---------------------------------------------------------------------------

def _call_ollama(prompt: str) -> str:
    try:
        from ollama import Client  # pip install ollama
        client = Client(host=OLLAMA_BASE)
        response = client.generate(model=OLLAMA_MODEL, prompt=prompt)
        return response["response"]
    except ImportError:
        raise RuntimeError(
            "Ollama Python package not installed. Run: pip install ollama"
        )
    except Exception as e:
        raise RuntimeError(f"Ollama error: {str(e)}")


# ---------------------------------------------------------------------------
# Groq backend
# ---------------------------------------------------------------------------

def _call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com and add it to .env"
        )
    try:
        from groq import Groq  # pip install groq
        client = Groq(api_key=GROQ_API_KEY)
        chat = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a SQLite SQL expert. "
                        "Always respond with ONLY a valid SQL SELECT statement. "
                        "No markdown, no explanation, no backticks."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,   # low temp = more deterministic SQL
            max_tokens=512,
        )
        return chat.choices[0].message.content
    except ImportError:
        raise RuntimeError(
            "Groq Python package not installed. Run: pip install groq"
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error: {str(e)}")


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def generate_sql(schema: str, question: str, error_feedback: str = "") -> str:
    """
    Generates a SQL query from a natural language question.
    Returns cleaned SQL string.
    Raises RuntimeError if LLM call fails.
    """
    prompt = build_prompt(schema, question, error_feedback)

    if LLM_PROVIDER == "ollama":
        raw = _call_ollama(prompt)
    elif LLM_PROVIDER == "groq":
        raw = _call_groq(prompt)
    else:
        raise RuntimeError(
            f"Unknown LLM_PROVIDER: '{LLM_PROVIDER}'. Use 'ollama' or 'groq'."
        )

    return clean_sql(raw)


def get_provider_info() -> dict:
    """Returns current provider config for display in UI."""
    if LLM_PROVIDER == "ollama":
        return {"provider": "Ollama (Local)", "model": OLLAMA_MODEL}
    return {"provider": "Groq (Free API)", "model": GROQ_MODEL}
