class Identity:
    def __init__(self, subject: str):
        self.subject = subject

    def id(self) -> str:
        return self.subject
