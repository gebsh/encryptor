import os
from encryptor import ROOT_DIR


BUFFER_SIZE = 1024
DEFAULT_SERVER_PORT = 40000
PUBLIC_KEY_DIR = "public"
PRIVATE_KEY_DIR = "private"
PUBLIC_KEY_PATH = os.path.join(PUBLIC_KEY_DIR, "pubkey.pem")
PRIVATE_KEY_PATH = os.path.join(PRIVATE_KEY_DIR, "privkey.pem")

# TODO: remove following constants.
ASSETS = os.path.join(ROOT_DIR, "assets/")
SEND_PUBLIC_KEY = os.path.join(ASSETS, "send_public.pem")
SEND_PRIVATE_KEY = os.path.join(ASSETS, "send_private.pem")
RECEIVE_PUBLIC_KEY = os.path.join(ASSETS, "receive_public.pem")
RECEIVE_PRIVATE_KEY = os.path.join(ASSETS, "receive_private.pem")
