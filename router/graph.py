from typing import TypedDict, Set
from langgraph.graph import StateGraph, END

from router.rules import rule_based_intent
from router.classifier import llm_intent_classifier

from memory.retrieval import get_memory_context, store_memory

from router.dependency import detect_dependency
from router.hybrid_executor import (
    sql_depends_on_rag,
    rag_depends_on_sql,
    independent_run
)


# -----------------------------
# Router State
# -----------------------------
class RouterState(TypedDict):
    question: str
    intents: Set[str]
    final: str


# -----------------------------
# Intent Detection Node
# -----------------------------
def detect_intent_node(state):
    question = state["question"]

    # Step 1: Rule-based intent detection
    intents = rule_based_intent(question)

    if intents != {"unknown"}:
        print(f"\n🟢 Intent decided by RULES → {intents}")

    # Step 2: If unclear, fallback to LLM classifier
    if intents == {"unknown"}:
        intents = llm_intent_classifier(question)
        print(f"\n🔵 Intent decided by LLM → {intents}")

    return {
        **state,
        "intents": intents,
        "final": ""
    }


# -----------------------------
# Routing Node (Memory + Dependency)
# -----------------------------
def route_node(state):

    question = state["question"]
    intents = state["intents"]

    # ✅ Step 1: Memory Retrieval FIRST
    memory_context = get_memory_context(question)

    if memory_context:
        print("🧠 Memory Match Found!")

        # Inject memory into query
        enriched_question = f"""
Previous Memory Context:
{memory_context}

Now answer the new question:
{question}
"""
    else:
        enriched_question = question

    # ✅ Step 2: Dependency Detection
    dependency = detect_dependency(question)
    print(f"⚡ Dependency detected → {dependency}")

    # -----------------------------
    # Greeting
    # -----------------------------
    if "greet" in intents:
        final = "Hello! How can I help you today?"

    # -----------------------------
    # Dependency Execution
    # -----------------------------
    elif dependency == "sql_depends_on_rag":
        final = sql_depends_on_rag(enriched_question)

    elif dependency == "rag_depends_on_sql":
        final = rag_depends_on_sql(enriched_question)

    else:
        final = independent_run(enriched_question, intents)

    # ✅ Step 3: Store Conversation in Memory
    store_memory(question, final)

    return {**state, "final": final}


# -----------------------------
# Finalize Node
# -----------------------------
def finalize_node(state: RouterState) -> RouterState:
    return state


# -----------------------------
# Build LangGraph Router
# -----------------------------
graph = StateGraph(RouterState)

graph.add_node("detect", detect_intent_node)
graph.add_node("route", route_node)
graph.add_node("finalize", finalize_node)

graph.set_entry_point("detect")

graph.add_edge("detect", "route")
graph.add_edge("route", "finalize")
graph.add_edge("finalize", END)

router_app = graph.compile()
