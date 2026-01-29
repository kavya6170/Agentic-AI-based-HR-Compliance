import re
from rapidfuzz import process
from sqlglot import parse_one, exp
from sql_pipeline.database import COLUMNS

def clean_sql(sql):
    return sql.replace("```sql", "").replace("```", "").strip()

def fix_columns(sql):
    for token in re.findall(r"[a-zA-Z_]+", sql):
        if token.lower() not in COLUMNS:
            best, score, _ = process.extractOne(token, COLUMNS)
            if score > 85:
                sql = sql.replace(token, best)
    return sql

def validate_sql(sql):
    tree = parse_one(sql)
    for node in tree.walk():
        if isinstance(node, (exp.Drop, exp.Delete, exp.Update, exp.Insert, exp.Alter)):
            raise ValueError("Unsafe SQL detected")
    return sql
