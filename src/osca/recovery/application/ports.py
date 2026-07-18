from pathlib import Path
from typing import Protocol


class EncryptionContainer(Protocol):
    container_id: str

    def encrypt(self, cleartext: Path, destination: Path, recipient: str) -> None: ...

    def decrypt(self, package: Path, cleartext: Path, identity: bytes) -> None: ...
