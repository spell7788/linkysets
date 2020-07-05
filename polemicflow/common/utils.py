from typing import Any


class Proxy:
    def __init__(self, wrappee: Any):
        self.wrappee = wrappee

    def __getattr__(self, name: str) -> Any:
        return getattr(self.wrappee, name)
