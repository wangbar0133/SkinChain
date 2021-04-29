# -*-coding:utf-8-*-
import hashlib

import ed25519


def hash_sha256(string):
    """哈希"""
    sha = hashlib.sha256()
    sha.update(string)
    return sha.hexdigest()


def file_hash(file_path):
    """对文件取哈希值"""
    byte = 1024
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(byte)
            if data:
                md5.update(data)
            else:
                break
    return md5.hexdigest()


def sign(string, password):
    """签名"""
    sig = bytes(password, encoding="utf8")
    sk = ed25519.SigningKey(sig, encoding="hex")
    sign_value = sk.sign(bytes(string, encoding='UTF-8'), encoding="base64")
    return str(sign_value)[2:-1]


def check_sign(string, sig, vkey_hex):
    """验证签名"""
    sig = bytes(sig, encoding="utf8")
    vkey_hex = bytes(vkey_hex, encoding="utf8")
    verifying_key = ed25519.VerifyingKey(vkey_hex, encoding="hex")
    try:
        verifying_key.verify(sig, bytes(string, encoding='UTF-8'), encoding="base64")
        result = True
    except ed25519.BadSignatureError:
        result = False
    return result


def check_hash(string, hash_value):
    """验证哈希值"""
    sha = hashlib.sha256()
    sha.update(string)
    return hash_value == sha.hexdigest()


def check_password(username, password):
    """检查账户密码是否正确，返回bool"""
    sig = bytes(password, encoding="utf8")
    vkey_hex = bytes(username, encoding="utf8")
    signature_key = ed25519.SigningKey(sig, encoding="hex")
    verifying_key = ed25519.VerifyingKey(vkey_hex, encoding="hex")
    return verifying_key == signature_key.get_verifying_key()


if __name__ == "__main__":
    path = r"C:\Users\Administrator.DESKTOP-35V3OQH\SkinChain\coins\fc503153dab068850d83a3e7dbb88585\1f0e6968fc800be658bbb21ef27c18af.jpeg"
    print(file_hash(path))

    # print(len("96cae35ce8a9b0244178bf28e4966c2ce1b8385723a96a6b838858cdd6ca0a1e"))

    pass
