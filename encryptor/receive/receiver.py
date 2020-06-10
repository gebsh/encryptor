import sys
import os
import hashlib
from encryptor import constants
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad

def create_keys(password):
    if os.path.exists(constants.RECEIVE_PRIVATE_KEY) and os.path.exists(
        os.path.abspath(constants.RECEIVE_PUBLIC_KEY)
    ):
        print("Decrypting private key...")
        pass_hash_key = hashlib.sha256(password.encode()).digest()
        print(pass_hash_key)

        file_in = open(constants.RECEIVE_PRIVATE_KEY, "rb")
        iv, encrypted_privkey = [ file_in.read(x) for x in (AES.block_size, -1) ]
        file_in.close()

        cipher_aes = AES.new(pass_hash_key, AES.MODE_CBC, iv)
        decypted_privkey = unpad(cipher_aes.decrypt(encrypted_privkey), AES.block_size)
        private_key = RSA.import_key(decypted_privkey)
        return private_key

    key = RSA.generate(2048)

    # Create private key.
    private_key = key.export_key()

    pass_hash_key = hashlib.sha256(password.encode()).digest()
    print(pass_hash_key)

    cipher_aes = AES.new(pass_hash_key, AES.MODE_CBC)
    encrypted_privkey = cipher_aes.encrypt(pad(private_key, AES.block_size))

    file_out = open(constants.RECEIVE_PRIVATE_KEY, "wb")
    [file_out.write(x) for x in (cipher_aes.iv, encrypted_privkey)]
    file_out.close()

    # Create public key.
    public_key = key.publickey().export_key()

    file_out = open(constants.RECEIVE_PUBLIC_KEY, "wb")
    file_out.write(public_key)
    file_out.close()


def decrypt_message(private_key):
    encrypted_message_path = os.path.join(constants.ASSETS, "encrypted_message.txt")
    decrypted_message_path = os.path.join(constants.ASSETS, "decrypted_message.txt")

    if not os.path.exists(encrypted_message_path):
        print("No data to decrypt")

        return

    print("Decrypting the message to assets/decrypted_message.txt")

    file_in = open(encrypted_message_path, "rb")
    mode = file_in.read(3)
    mode = mode.decode('utf-8')
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
