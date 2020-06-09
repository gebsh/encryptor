import sys
import os
from encryptor import constants
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad

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

def encrypt_message(message, mode):
    encrypted_message_path = os.path.join(constants.ASSETS, "encrypted_message.txt")

    if not os.path.exists(constants.RECEIVE_PUBLIC_KEY):
        print("Could not encrypt message, receive public key does not exist")

        return

    print("Encrypting the message to assets/encrypted_message.txt \nmode: ", mode)

    recipient_key = RSA.import_key(open(constants.RECEIVE_PUBLIC_KEY).read())
    session_key = os.urandom(16)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    file_out = open(encrypted_message_path, "wb")

    cipher_aes = {
        'ECB': AES.new(session_key, AES.MODE_ECB),
        'CBC': AES.new(session_key, AES.MODE_CBC),
        'OFB': AES.new(session_key, AES.MODE_OFB),
        'CFB': AES.new(session_key, AES.MODE_CFB)
    }[mode]

    ciphertext = cipher_aes.encrypt(pad(message, AES.block_size))

    if mode == 'ECB':
        [file_out.write(x) for x in (enc_session_key, ciphertext)]
        file_out.close()
    else:
        [file_out.write(x) for x in (enc_session_key, cipher_aes.iv, ciphertext)]
        file_out.close()
