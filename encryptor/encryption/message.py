class Message:
    """A message sent between applications."""

    def __init__(self, content: str, sender: str) -> None:
        self.content = content
        self.sender = sender
