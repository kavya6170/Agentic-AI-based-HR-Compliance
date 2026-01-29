import re
from rag_pipeline.app import app as rag_app
from sql_pipeline.agent import analytical_agent


def run_rag(question: str):
    return rag_app.invoke({
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
    })["final"]


def run_sql(question: str):
    return analytical_agent(question)


# -----------------------------
# SQL depends on RAG
# -----------------------------
def sql_depends_on_rag(question: str):

    rag_answer = run_rag(question)

    # Extract numeric limits like "12 days"
    match = re.search(r"maximum of (\d+)", rag_answer)

    if match:
        limit = match.group(1)

        # Inject into SQL question
        sql_question = f"{question}. Policy limit is {limit}."

        sql_answer = run_sql(sql_question)

        return f"""
📌 Policy Info (RAG):
{rag_answer}

📊 Data Result (SQL):
{sql_answer}
"""

    return f"""
📌 Policy Answer:
{rag_answer}

❌ Could not extract numeric limit for SQL.
"""


# -----------------------------
# RAG depends on SQL
# -----------------------------
def rag_depends_on_sql(question: str):

    sql_answer = run_sql(question)

    # Feed SQL output into RAG context
    rag_question = f"""
User asked: {question}

Dataset insight:
{sql_answer}

Now explain based on HR policies.
"""

    rag_answer = run_rag(rag_question)

    return f"""
📊 Dataset Insight (SQL):
{sql_answer}

📌 Policy Explanation (RAG):
{rag_answer}
"""


# -----------------------------
# Independent execution
# -----------------------------
def independent_run(question: str, intents: set):

    outputs = []

    if "rag" in intents:
        outputs.append(run_rag(question))

    if "sql" in intents:
        outputs.append(run_sql(question))

    return "\n\n".join(outputs)
