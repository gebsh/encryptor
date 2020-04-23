import sys
import os
from encryptor import constants
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP


def create_keys():
    if os.path.exists(constants.SEND_PRIVATE_KEY) and os.path.exists(
        constants.SEND_PUBLIC_KEY
    ):
        print("Keys already exist, skipping creation...")

        return

    key = RSA.generate(2048)

    # Create private key.
    private_key = key.export_key()

    file_out = open(constants.SEND_PRIVATE_KEY, "wb")
    file_out.write(private_key)
    file_out.close()

    # Create public key.
    public_key = key.publickey().export_key()

    file_out = open(constants.SEND_PUBLIC_KEY, "wb")
    file_out.write(public_key)
    file_out.close()


def encrypt_message(message):
    encrypted_message_path = os.path.join(constants.ASSETS, "encrypted_message.txt")

    if not os.path.exists(constants.RECEIVE_PUBLIC_KEY):
        print("Could not encrypt message, receive public key does not exist")

        return

    print("Encrypting the message to assets/encrypted_message.txt")

    recipient_key = RSA.import_key(open(constants.RECEIVE_PUBLIC_KEY).read())
    session_key = os.urandom(16)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    file_out = open(encrypted_message_path, "wb")
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message)

    [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    file_out.close()
