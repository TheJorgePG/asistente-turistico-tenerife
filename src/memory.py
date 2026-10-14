class ConversationalMemory:
    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > (self.max_turns * 2):
            self.history = self.history[-self.max_turns * 2:]

    def get_context(self):
        return self.history