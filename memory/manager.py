from memory.short_term import ShortTermMemory
from memory.long_term import save, search


class MemoryManager:

    def __init__(self):
        self.stm = ShortTermMemory(limit=20)

    def add_chat(self, question, answer):
        """
        Add chat into STM.
        If STM overflows → flush into SQLite.
        """

        flushed_entry = self.stm.add(question, answer)

        if flushed_entry:
            print("⚡ STM full → flushing oldest chat into SQLite...")
            save(flushed_entry)

    def retrieve(self, question):
        """
        Retrieve memory:
        1. STM first
        2. SQLite LTM second
        """

        # -------------------
        # Search STM
        # -------------------
        for chat in reversed(self.stm.all()):
            if question.lower() in chat["question"].lower():
                return f"""
🧠 Found in STM:
Q: {chat['question']}
A: {chat['answer']}
"""

        # -------------------
        # Search LTM
        # -------------------
        results = search(question)

        if results:
            q, a = results[0]
            return f"""
🧠 Found in SQLite LTM:
Q: {q}
A: {a}
"""

        return None
