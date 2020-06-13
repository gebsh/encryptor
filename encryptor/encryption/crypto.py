import os
import random
import string
from typing import cast, Any
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from .mode import EncryptionMode


def encrypt(data: bytes, mode: EncryptionMode, rec_pubkey: RSA.RsaKey) -> bytes:
    """Encrypt given bytes using a specified encryption mode and receipent key."""

    session_key = os.urandom(16)
    cipher_rsa = PKCS1_OAEP.new(rec_pubkey)
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = {
        EncryptionMode.ECB: AES.new(session_key, AES.MODE_ECB),
        EncryptionMode.CBC: AES.new(session_key, AES.MODE_CBC),
        EncryptionMode.CFB: AES.new(session_key, AES.MODE_CFB),
        EncryptionMode.OFB: AES.new(session_key, AES.MODE_OFB)
    }[mode]
    ciphertext: bytes = cipher_aes.encrypt(pad(data, AES.block_size))

    if mode == EncryptionMode.ECB:
        return enc_session_key + ciphertext

    return enc_session_key + cast(bytes, cast(Any, cipher_aes).iv) + ciphertext


def decrypt(data: bytes, mode: EncryptionMode, rec_privkey: RSA.RsaKey) -> bytes:
    """Decrypt given bytes using a specified encryption mode and."""

    key_len = rec_privkey.size_in_bytes()
    enc_session_key = data[:key_len]
    cipher_rsa = PKCS1_OAEP.new(rec_privkey)

    if mode == 'EncryptionMode.ECB':
        iv = None
        ciphertext = data[key_len:]
    else:
        iv_end = key_len + AES.block_size
        iv = data[key_len:iv_end]
        ciphertext = data[iv_end:]

    try:
        session_key = cipher_rsa.decrypt(enc_session_key)
    except ValueError:
        session_key = os.urandom(16)

    try:
        cipher_aes = {
            'EncryptionMode.ECB': AES.new(session_key, AES.MODE_ECB),
            'EncryptionMode.CBC': AES.new(session_key, AES.MODE_CBC, cast(bytes, iv)),
            'EncryptionMode.CFB': AES.new(session_key, AES.MODE_CFB, cast(bytes, iv)),
            'EncryptionMode.OFB': AES.new(session_key, AES.MODE_OFB, cast(bytes, iv))
        }[mode]
    except KeyError:
        print("KeyError")

    try:
        data = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)
    except ValueError:
        data = (
            "".join(
                random.SystemRandom().choice(string.printable)
                for _ in range(random.randint(5, 100))
            )
        ).encode("utf-8")

    return data
