import os
import inspect
from encryptor import ROOT_DIR


ASSETS = os.path.join(ROOT_DIR, "assets/")
SEND_PUBLIC_KEY = os.path.join(ASSETS, "send_public.pem")
SEND_PRIVATE_KEY = os.path.join(ASSETS, "send_private.pem")
RECEIVE_PUBLIC_KEY = os.path.join(ASSETS, "receive_public.pem")
RECEIVE_PRIVATE_KEY = os.path.join(ASSETS, "receive_private.pem")
