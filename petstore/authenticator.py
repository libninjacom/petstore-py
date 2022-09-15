import os
from typing import Dict, Any


class PetstoreAuthenticator:
    def __init__(self):
        pass

    def authenticate(
        self, headers: Dict[str, str], params: Dict[str, str], data: Dict[str, Any]
    ) -> None:
        pass

    @classmethod
    def from_env(cls) -> "PetstoreAuthenticator":
        return cls()
