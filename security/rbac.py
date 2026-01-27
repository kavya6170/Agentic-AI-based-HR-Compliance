def enforce_rbac(sql: str, user: dict):

    role = user["role"]
    emp_id = user["emp_id"]

    sql_lower = sql.lower()

    # 🚫 Employees and managers cannot modify database
    if role in ["employee", "manager"]:
        forbidden = ["delete", "update", "insert", "drop", "alter"]

        if any(word in sql_lower for word in forbidden):
            raise ValueError("❌ You are not allowed to modify employee data.")

    # ✅ Employee → Only own row
    if role == "employee":
        if "where" in sql_lower:
            sql += f" AND employeeid = {emp_id}"
        else:
            sql += f" WHERE employeeid = {emp_id}"

    # ✅ Manager → Own + Team
    elif role == "manager":
        if "where" in sql_lower:
            sql += f" AND (employeeid = {emp_id} OR manager_id = {emp_id})"
        else:
            sql += f" WHERE (employeeid = {emp_id} OR manager_id = {emp_id})"

    # ✅ Admin → Full access
    return sql
