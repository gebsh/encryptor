import os


METAHEADER_LEN = 8
BUFFER_SIZE = 1024
DEFAULT_SERVER_PORT = 40000
PUBLIC_KEY_DIR = "public"
PRIVATE_KEY_DIR = "private"
PUBLIC_KEY_PATH = os.path.join(PUBLIC_KEY_DIR, "pubkey.pem")
PRIVATE_KEY_PATH = os.path.join(PRIVATE_KEY_DIR, "privkey.pem")
