"""
db_engine.py — SQLite connection, schema fetching, query execution
"""

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "querymind.db")


def get_db_path() -> str:
    return DB_PATH


def get_schema(db_path: str = DB_PATH) -> str:
    """
    Dynamically reads all tables and their columns from the SQLite DB.
    Returns a clean string representation for the LLM prompt.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        conn.close()
        return "No tables found in database."

    schema_lines = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_descriptions = []
        for col in cols:
            # col: (cid, name, type, notnull, dflt_value, pk)
            pk_marker = " [PK]" if col[5] else ""
            col_descriptions.append(f"{col[1]} {col[2]}{pk_marker}")
        schema_lines.append(f"Table '{table}': {', '.join(col_descriptions)}")

    conn.close()
    return "\n".join(schema_lines)


def get_schema_detailed(db_path: str = DB_PATH) -> str:
    """
    Returns schema as CREATE TABLE statements — used for display in UI.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    statements = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return "\n\n".join(statements)


def execute_query(sql: str, db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Executes a SELECT SQL query and returns a DataFrame.
    Raises ValueError with a clean message on failure.
    """
    sql = sql.strip()

    # Safety: only allow SELECT statements
    if not sql.upper().startswith("SELECT"):
        raise ValueError(
            "Only SELECT queries are allowed. "
            "The generated query was not a SELECT statement."
        )

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        raise ValueError(f"Query execution failed: {str(e)}")
    finally:
        conn.close()


def db_exists(db_path: str = DB_PATH) -> bool:
    return os.path.exists(db_path)
