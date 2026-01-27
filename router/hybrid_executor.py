from rag_pipeline.app import app as rag_app
from sql_pipeline.agent import analytical_agent


# -----------------------------
# Run RAG Pipeline
# -----------------------------
def run_rag(question: str):

    rag_state = rag_app.invoke({
        "question": question,
        "retrieved": [],
        "reranked": [],
        "categories": {
            "mandatory": [],
            "restriction": [],
            "penalty": [],
            "procedure": [],
            "general": []
        },
        "context": "",
        "answer": "",
        "sources": set(),
        "hallucination_check": {},
        "retry_count": 0
    })

    return rag_state.get("final", rag_state.get("answer", "No response"))


# -----------------------------
# Run SQL Pipeline (RBAC enforced)
# -----------------------------
def run_sql(question: str, user: dict):

    if user is None:
        return "❌ Unauthorized SQL access (user missing)."

    return analytical_agent(question, user)


# -----------------------------
# Dependency Execution
# -----------------------------
def sql_depends_on_rag(question: str, user: dict):
    """
    First run RAG to get policy info,
    then SQL for employee data.
    """

    rag_answer = run_rag(question)

    combined_question = f"""
Policy Context:
{rag_answer}

Now answer analytically using employee database:
{question}
"""

    sql_answer = run_sql(combined_question, user)

    return f"{rag_answer}\n\n📊 Analytical Result:\n{sql_answer}"


def rag_depends_on_sql(question: str, user: dict):
    """
    First run SQL to get numbers,
    then RAG to explain policy implications.
    """

    sql_answer = run_sql(question, user)

    combined_question = f"""
Employee Data Result:
{sql_answer}

Now answer using policy documents:
{question}
"""

    rag_answer = run_rag(combined_question)

    return f"{sql_answer}\n\n📘 Policy Explanation:\n{rag_answer}"


# -----------------------------
# Independent Execution
# -----------------------------
def independent_run(question: str, intents: set, user: dict):

    outputs = []

    if "rag" in intents:
        outputs.append("📘 Policy Answer:\n" + run_rag(question))

    if "sql" in intents:
        outputs.append("📊 Data Answer:\n" + run_sql(question, user))

    return "\n\n".join(outputs)
