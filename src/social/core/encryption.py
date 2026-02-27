import json

from cryptography.fernet import Fernet

from social.config import get_settings

ENCRYPTED_MARKER = "_encrypted"


def _get_fernet() -> Fernet | None:
    key = get_settings().encryption_key
    if not key:
        return None
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_credentials(data: dict) -> dict:
    f = _get_fernet()
    if f is None:
        return data
    plaintext = json.dumps(data).encode()
    ciphertext = f.encrypt(plaintext).decode()
    return {ENCRYPTED_MARKER: ciphertext}


def decrypt_credentials(data: dict) -> dict:
    if ENCRYPTED_MARKER not in data:
        return data
    f = _get_fernet()
    if f is None:
        return data
    ciphertext = data[ENCRYPTED_MARKER].encode()
    plaintext = f.decrypt(ciphertext)
    return json.loads(plaintext)
