from sql_pipeline.nl_to_sql import nl_to_sql
from sql_pipeline.sql_utils import clean_sql, fix_columns, validate_sql
from sql_pipeline.database import con
from sql_pipeline.llm import qwen
from security.rbac import enforce_rbac
from sql_pipeline.sql_utils import (
    clean_sql,
    fix_table_names,
    fix_columns,
    validate_sql
)

def analytical_agent(question, user):

    sql = nl_to_sql(question)
    if not sql:
        return "❌ SQL not generated."

    sql = clean_sql(sql)
    sql = fix_table_names(sql) 
    sql = fix_columns(sql)

    print("\n🧾 SQL after fix:\n", sql)

    try:
        validate_sql(sql)

        # ✅ RBAC FILTER APPLIED HERE
        sql = enforce_rbac(sql, user)

        print("\n🔐 SQL After RBAC Enforcement:\n", sql)

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
