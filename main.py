from router.graph import router_app
from memory.manager import MemoryManager
from memory.long_term import init_ltm

# Initialize SQLite DB at startup
init_ltm()

memory = MemoryManager()

print("🤖 HR COMPLIANCE SMART ASSISTANT")

while True:
    user_query = input("❓ Ask: ").strip()
    if user_query.lower() == "exit":
        break

    # 🧠 MEMORY LOOKUP
    memory_hit, source = memory.recall(user_query)

    memory_context = ""
    if memory_hit:
        memory_context = f"""
Previous related conversation ({source}):
Q: {memory_hit['question']}
A: {memory_hit['answer']}
"""

    # 🚦 ROUTER INVOCATION
    result = router_app.invoke({"question": user_query})

    print("\n" + "="*80)
    print("🧠 RESPONSE")
    print("-"*80)
    print(result.get("final", "❌ No response generated"))
    print("="*80 + "\n")



    answer = result.get("final", "No response")

    print("\n🧠 RESPONSE:\n", answer)
    print("="*80)

    # 💾 STORE MEMORY
    memory.store(user_query, answer)
