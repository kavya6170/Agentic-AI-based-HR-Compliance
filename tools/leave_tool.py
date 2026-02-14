import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router.hybrid_executor import run_rag, run_sql
from sql_pipeline.database import con
import re

def get_leave_balance(employee_id: int, leave_type: str = "sick leave"):
    """
    Calculates the remaining leave balance for an employee.
    
    1. Gets policy limit via RAG.
    2. Gets used leaves via SQL.
    3. Returns the difference.
    """
    
    # 1. Get Policy Limit via RAG
    rag_query = f"What is the maximum allowed {leave_type} days per year according to the HR policy?"
    rag_answer = run_rag(rag_query)
    
    # Extract numeric value (reusing logic from hybrid_executor or similar)
    from router.hybrid_executor import extract_numeric_policy_value
    policy_limit = extract_numeric_policy_value(rag_answer)
    
    if policy_limit is None:
        return f"❌ Could not determine the policy limit from documents. RAG Answer: {rag_answer}"
    
    # 2. Get Used Leaves via SQL
    # Note: For now mapping all to sickleaveslastyear as per schema analysis
    # In a real scenario, this would map leave_type to specific columns
    column_map = {
        "sick leave": "sickleaveslastyear",
        "sick": "sickleaveslastyear",
        # Add more mappings as columns are identified
    }
    
    target_col = column_map.get(leave_type.lower(), "sickleaveslastyear")
    
    sql = f"SELECT employeename, {target_col} FROM employee WHERE employeeid = {employee_id}"
    
    try:
        df = con.execute(sql).fetchdf()
        if df.empty:
            return f"❌ Employee with ID {employee_id} not found."
        
        emp_name = df.iloc[0]['employeename']
        used = int(df.iloc[0][target_col])
        balance = policy_limit - used
        
        return {
            "employee_id": employee_id,
            "employee_name": emp_name,
            "leave_type": leave_type,
            "policy_limit": policy_limit,
            "used_leaves": used,
            "balance": balance,
            "source_policy": rag_answer
        }
        
    except Exception as e:
        return f"❌ SQL Error: {str(e)}"

if __name__ == "__main__":
    # Test run
    print("Testing Leave Tool for Employee 2002...")
    result = get_leave_balance(2002, "sick leave")
    import json
    print(json.dumps(result, indent=2))
