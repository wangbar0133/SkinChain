import time

from src.bin.encrypt import sign, hash_sha256


class Block(object):
    """区块对象"""

    def __init__(self, index, sender, recive, pr_block_hash, coin, mesg):
        self.header = {
            "index": index,
            "pr_block_hash": pr_block_hash,
            "timestamp": str(time.time()),
            "sender": sender
        }
        self.tran = {
            "recive": recive,
            "coin": coin,
            "mesg": mesg
        }
        self.sign_value = sign(bytes(self.header.__str__() + self.tran.__str__(), encoding='UTF-8'), sender)
        self.block_hash = hash_sha256(self.header.__str__() + self.tran.__str__() + self.sign_value)
        self.block = {
            "header": self.header,
            "tran": self.tran,
            "sign": self.sign_value,
            "block_hash": self.block_hash
        }

    def print_block(self):
        print(self.block)

    def add_tran(self, trans_list):
        self.block["trans_list"].append(trans_list)
