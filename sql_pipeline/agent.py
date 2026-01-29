from sql_pipeline.nl_to_sql import nl_to_sql
from sql_pipeline.sql_utils import clean_sql, fix_columns, validate_sql
from sql_pipeline.database import con
from sql_pipeline.llm import qwen

def analytical_agent(question):
    sql = nl_to_sql(question)
    if not sql:
        return "❌ SQL not generated."

    sql = clean_sql(sql)
    sql = fix_columns(sql)
    sql = normalize_sql(sql)
    print("\n🧾 SQL after fix:\n", sql)

    try:
        validate_sql(sql)
        df = con.execute(sql).fetchdf()
    except Exception as e:
        return f"❌ {e}"

    if df.empty:
        return "No data found."

    return qwen(f"""
User question: {question}
SQL result:
{df.to_string(index=False)}
Explain simply.
""")

def normalize_sql(sql: str):
    """Fix MySQL-style backticks for DuckDB"""
    return sql.replace("`", "")
