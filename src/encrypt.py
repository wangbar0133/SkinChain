import hashlib
import ed25519


def tran_16_to_2(string):
    """十六进制转二进制"""
    dict_bin = {
                '0': '0000',
                '1': '0001',
                '2': '0010',
                '3': '0011',
                '4': '0100',
                '5': '0101',
                '6': '0110',
                '7': '0111',
                '8': '1000',
                '9': '1001',
                'a': '1010',
                'b': '1011',
                'c': '1100',
                'd': '1101',
                'e': '1110',
                'f': '1111'
                }
    list_arr = []
    for item in string:
            dict_bin = dict_bin
            list_arr = list_arr + dict_bin[item]
    return list_arr


def hash_sha256(string):
    """哈希"""
    sha = hashlib.sha256()
    sha.update(string)
    return sha.hexdigest()


def file_hash(file_path):
    """对文件取哈希值"""
    Bytes = 1024
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(Bytes)
            if data:
                md5.update(data)
            else:
                break
    return md5.hexdigest()


def sign(string, responsible):
    """
    :param string: str
    :param responsible: responsible对象
    :return: responsible的签名密钥对string的签名
    """
    SigningKey = responsible.SigningKey
    sign = SigningKey.sign(bytes(string, encoding='UTF-8'), encoding="base64")
    return str(sign)[2:-1]


def check_sign(string, sig, vkey_hex):
    """
    :param string: str 验签字符串
    :param sig: 签名
    :param vkey_hex: 用户名
    """
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
