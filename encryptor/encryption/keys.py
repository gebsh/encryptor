import os
from Crypto.PublicKey import RSA
from encryptor import constants


def keys_exist(keys_dir: str) -> bool:
    """Check if keys exist."""

    pubkey_path = os.path.join(keys_dir, constants.PUBLIC_KEY_PATH)
    privkey_path = os.path.join(keys_dir, constants.PRIVATE_KEY_PATH)

    return os.path.exists(pubkey_path) and os.path.exists(privkey_path)


def create_keys(password: str, keys_dir: str) -> None:
    """Create public and private keys."""

    if not os.path.exists(constants.PUBLIC_KEY_DIR):
        os.mkdir(constants.PUBLIC_KEY_DIR)

    if not os.path.exists(constants.PRIVATE_KEY_DIR):
        os.mkdir(constants.PRIVATE_KEY_DIR)

    pubkey_path = os.path.join(keys_dir, constants.PUBLIC_KEY_PATH)
    privkey_path = os.path.join(keys_dir, constants.PRIVATE_KEY_PATH)
    key = RSA.generate(2048)
    public_key = key.publickey().export_key()
    private_key = key.export_key(passphrase=password)
    file_out = open(privkey_path, "wb")
    file_out.write(private_key)
    file_out.close()

    file_out = open(pubkey_path, "wb")

    file_out.write(public_key)
    file_out.close()


def get_public_key(keys_dir: str) -> RSA.RsaKey:
    """Get public key of a user."""

    key_file = open(os.path.join(keys_dir, constants.PUBLIC_KEY_PATH), "rb")

    return RSA.import_key(key_file.read())


def get_private_key(password: str, keys_dir: str) -> RSA.RsaKey:
    """Get private key of a user."""

    key_file = open(os.path.join(keys_dir, constants.PRIVATE_KEY_PATH), "rb")
    encrypted_privkey = key_file.read()
    key_file.close()
    private_key = RSA.import_key(encrypted_privkey, passphrase=password)
    return private_key
