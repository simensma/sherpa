from Crypto.Cipher import AES
from core import pkcs7

import base64

def encrypt(key, plaintext):
    padded_text = pkcs7.encode(plaintext, len(key))
    cipher = AES.new(key, AES.MODE_ECB)
    msg = cipher.encrypt(padded_text)
    encoded = base64.b64encode(msg)
    return encoded

def decrypt(key, encoded):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = base64.b64decode(encoded)
    msg_padded = cipher.decrypt(ciphertext)
    msg = pkcs7.decode(msg_padded, len(key))
    return msg
