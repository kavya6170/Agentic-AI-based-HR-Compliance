import re
from sql_pipeline.llm import llm_call
from sql_pipeline.database import COLUMNS

def nl_to_sql(question):
    prompt = f"""
You are a SQL-only generator.

Table: employees
Columns: {COLUMNS}

Rules:
- Output ONLY SQL
- Must start with SELECT
- Output ONLY DuckDB compatible SQL
- only use these columns and table given
- Do NOT use backticks (`), use plain column names

Question: {question}

SQL:
"""
    out = llm_call(prompt)
    m = re.search(r"(select .*?$)", out, re.I | re.S)
    return m.group(1).strip() if m else None
