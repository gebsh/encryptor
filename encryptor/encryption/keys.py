from pathlib import Path
from Crypto.PublicKey import RSA
from encryptor import constants


def keys_exist(keys_dir: Path) -> bool:
    """Check if keys exist."""

    pubkey_path: Path = keys_dir / constants.PUBLIC_KEY_PATH
    privkey_path: Path = keys_dir / constants.PRIVATE_KEY_PATH

    return pubkey_path.exists() and privkey_path.exists()


def create_keys(keys_dir: Path, passphrase: str) -> None:
    """Create public and private keys."""

    pubkey_dir: Path = keys_dir / constants.PUBLIC_KEY_DIR
    pubkey_path: Path = keys_dir / constants.PUBLIC_KEY_PATH
    privkey_dir: Path = keys_dir / constants.PRIVATE_KEY_DIR
    privkey_path: Path = keys_dir / constants.PRIVATE_KEY_PATH
    key = RSA.generate(2048)
    pubkey = key.publickey().export_key()
    privkey = key.export_key(passphrase=passphrase)

    pubkey_dir.mkdir(parents=True, exist_ok=True)
    privkey_dir.mkdir(parents=True, exist_ok=True)
    pubkey_path.write_bytes(pubkey)
    privkey_path.write_bytes(privkey)


def get_public_key(keys_dir: Path) -> RSA.RsaKey:
    """Get public key of a user."""

    pubkey_path: Path = keys_dir / constants.PUBLIC_KEY_PATH

    return RSA.import_key(pubkey_path.read_bytes())


def get_private_key(keys_dir: Path, passphrase: str) -> RSA.RsaKey:
    """Get private key of a user."""

    privkey_path: Path = keys_dir / constants.PRIVATE_KEY_PATH

    return RSA.import_key(privkey_path.read_bytes(), passphrase=passphrase)
