import hashlib

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
    for item in string:
            dictBin = dict_bin
            listArr = listArr + dictBin[item]
    return self.listArr

def hash(string):
    """哈希"""
    sha = hashlib.sha256()
    sha.update(string)
    return sha.hexdigest()

def sign(self, string, responsible):
    '''
    :param string: str
    :param responsible: responsible对象
    :return: responsible的签名密钥对string的签名
    '''
    SigningKey = responsible.SigningKey
    sign = SigningKey.sign(bytes(string, encoding='UTF-8'), encoding="base64")
    return str(sign)[2:-1]    