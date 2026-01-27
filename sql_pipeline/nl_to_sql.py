from sql_pipeline.database import TABLES, TABLE_COLUMNS
from sql_pipeline.llm import qwen


def nl_to_sql(question):

    schema_text = ""

    for table in TABLES:
        schema_text += f"\nTable: {table}\nColumns: {TABLE_COLUMNS[table]}\n"

    prompt = f"""
You are a SQL-only generator.

Available Database Schema:
{schema_text}

Rules:
- Output ONLY SQL
- Must start with SELECT
- Use correct table names exactly as given

Question: {question}

SQL:
"""

    return qwen(prompt)
