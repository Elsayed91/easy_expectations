from textwrap import dedent


class ConversationFlow:
    def __init__(self):
        self.flow = []

    def add_message(self, role, content, auto_dedent=True):
        if auto_dedent:
            content = dedent(content)
        self.flow.append({"role": role, "content": content})

    def get_flow(self):
        return self.flow

    @classmethod
    def from_messages(cls, messages):
        """
        flow_instance = ConversationFlow.from_messages(messages)
        print(flow_instance.get_flow())
        """
        instance = cls()
        for message in messages:
            instance.add_message(message["role"], message["content"])
        return instance
