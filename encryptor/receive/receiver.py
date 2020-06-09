import sys
import os
from encryptor import constants
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad

def create_keys():
    if os.path.exists(constants.RECEIVE_PRIVATE_KEY) and os.path.exists(
        os.path.abspath(constants.RECEIVE_PUBLIC_KEY)
    ):
        print("Keys already exist, skipping creation...")

        return

    key = RSA.generate(2048)

    # Create private key.
    private_key = key.export_key()

    file_out = open(constants.RECEIVE_PRIVATE_KEY, "wb")
    file_out.write(private_key)
    file_out.close()

    # Create public key.
    public_key = key.publickey().export_key()

    file_out = open(constants.RECEIVE_PUBLIC_KEY, "wb")
    file_out.write(public_key)
    file_out.close()


def decrypt_message(mode):
    encrypted_message_path = os.path.join(constants.ASSETS, "encrypted_message.txt")
    decrypted_message_path = os.path.join(constants.ASSETS, "decrypted_message.txt")

    if not os.path.exists(encrypted_message_path):
        print("No data to decrypt")

        return

    print("Decrypting the message to assets/decrypted_message.txt")

    file_in = open(encrypted_message_path, "rb")
    private_key = RSA.import_key(open(constants.RECEIVE_PRIVATE_KEY).read())
    if mode == 'ECB':
        enc_session_key, ciphertext = [
            file_in.read(x) for x in (private_key.size_in_bytes(), -1)
        ]
    else:
        enc_session_key, iv, ciphertext = [
            file_in.read(x) for x in (private_key.size_in_bytes(), AES.block_size, -1)
        ]
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    if mode == 'ECB':
        cipher_aes = AES.new(session_key, AES.MODE_ECB)
    else:
        cipher_aes = {
            'CBC': AES.new(session_key, AES.MODE_CBC, iv),
            'OFB': AES.new(session_key, AES.MODE_OFB, iv),
            'CFB': AES.new(session_key, AES.MODE_CFB, iv)
        }[mode]

    data = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)
    file_out = open(decrypted_message_path, "w")

    file_out.write(data.decode("utf-8"))
    file_in.close()
    file_out.close()
