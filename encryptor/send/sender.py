import sys
import os
from encryptor import constants
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad

class Sender:
    def __init__(self):
        self.create_keys()

    def create_keys(self):
        if os.path.exists(constants.SEND_PRIVATE_KEY) and os.path.exists(
            constants.SEND_PUBLIC_KEY
        ):
            print("Keys already exist, skipping creation...")
            return

        self.key = RSA.generate(2048)

        # Create private key.
        self.private_key = self.key.export_key()

        self.file_out = open(constants.SEND_PRIVATE_KEY, "wb")
        self.file_out.write(self.private_key)
        self.file_out.close()

        # Create public key.
        self.public_key = self.key.publickey().export_key()

        self.file_out = open(constants.SEND_PUBLIC_KEY, "wb")
        self.file_out.write(self.public_key)
        self.file_out.close()

    def encrypt_message(self, message, mode):
        self.encrypted_message_path = os.path.join(constants.ASSETS, "encrypted_message.txt")

        if not os.path.exists(constants.RECEIVE_PUBLIC_KEY):
            print("Could not encrypt message, receive public key does not exist")
            return

        print("Encrypting the message to assets/encrypted_message.txt \nmode: ", mode)

        self.recipient_key = RSA.import_key(open(constants.RECEIVE_PUBLIC_KEY).read())
        self.session_key = os.urandom(16)
        self.cipher_rsa = PKCS1_OAEP.new(self.recipient_key)
        self.enc_session_key = self.cipher_rsa.encrypt(self.session_key)
        self.file_out = open(self.encrypted_message_path, "wb")

        self.cipher_aes = {
            'ECB': AES.new(self.session_key, AES.MODE_ECB),
            'CBC': AES.new(self.session_key, AES.MODE_CBC),
            'OFB': AES.new(self.session_key, AES.MODE_OFB),
            'CFB': AES.new(self.session_key, AES.MODE_CFB)
        }[mode]

        self.ciphertext = self.cipher_aes.encrypt(pad(message, AES.block_size))

        if mode == 'ECB':
            [self.file_out.write(x) for x in (mode.encode('utf-8'), self.enc_session_key, self.ciphertext)]
            self.file_out.close()
        else:
            [self.file_out.write(x) for x in (mode.encode('utf-8'), self.enc_session_key, self.cipher_aes.iv, self.ciphertext)]
            self.file_out.close()
