import duckdb, pandas as pd

con = duckdb.connect()

df = pd.read_csv(r"C:/Users/karan/Downloads/HR compliance/HR compliance/data/employees.csv")
df.columns = df.columns.str.lower().str.replace(" ", "_")
con.register("employees", df)

COLUMNS = df.columns.tolist()
