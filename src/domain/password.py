import bcrypt


class Password:
    def __init__(self, plain: str):
        self.plain = plain

    def hash(self) -> str:
        return bcrypt.hashpw(self.plain.encode(), bcrypt.gensalt()).decode()

    def matches(self, hash: str) -> bool:
        return bcrypt.checkpw(self.plain.encode(), hash.encode())
