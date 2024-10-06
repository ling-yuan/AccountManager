from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from tools.config import Config


class Cryption:

    def __init__(self) -> None:
        self._config = Config()

    @property
    def key(self) -> bytes:
        if not self._config.key:
            tmp_key = self._generate_key()
            self._config.key = tmp_key
        return self._config.key

    @key.setter
    def key(self, value: bytes) -> None:
        self._config.key = value

    def _generate_key(self, b: bytes = None) -> bytes:
        if b and len(b) != 16:
            raise ValueError("Key length must be 16 bytes")
        self._config.key = get_random_bytes(16) if b is None else b
        return self._config.key

    def encrypt_bytes(self, input_file_bytes: bytes):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(input_file_bytes)
        return cipher.nonce, ciphertext, tag

    def encrypt_file(self, file_path: str):
        with open(file_path, "rb") as f:
            input_file_bytes = f.read()
        nonce, ciphertext, tag = self.encrypt_bytes(input_file_bytes)
        s = nonce + tag + ciphertext
        return s

    def decrypt_bytes(self, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext

    def dectypt_file(self, file_path: str) -> bytes:
        with open(file_path, "rb") as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        return self.decrypt_bytes(nonce, ciphertext, tag)
