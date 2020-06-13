from pathlib import PurePath


METAHEADER_LEN = 8
BUFFER_SIZE = 1024
DEFAULT_SERVER_PORT = 40000
PUBLIC_KEY_DIR = PurePath("public")
PRIVATE_KEY_DIR = PurePath("private")
PUBLIC_KEY_PATH = PUBLIC_KEY_DIR / "pubkey.pem"
PRIVATE_KEY_PATH = PRIVATE_KEY_DIR / "privkey.pem"
