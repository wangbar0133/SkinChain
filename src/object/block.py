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
        self.sign_value = sign(self.header.__str__() + self.tran.__str__(), sender)
        self.block_hash = hash_sha256((self.header.__str__() + self.tran.__str__() + self.sign_value).encode("utf8"))
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


if __name__ == "__main__":
    """
    block = Block(index=0,
                  sender="eb1d2b43aad8cf60ff9911a894f80ec4f4befccc6c61901d2cc72aac1b1d89d2",
                  recive="eb1d2b43aad8cf60ff9911a894f80ec4f4befccc6c61901d2cc72aac1b1d89d2",
                  pr_block_hash="asdasdad",
                  coin="asdad",
                  mesg="")
    print(block.header)"""

    """
    string = {
            "index": 0,
            "pr_block_hash": "asdasdad",
            "timestamp": str(time.time()),
            "sender": "eb1d2b43aad8cf60ff9911a894f80ec4f4befccc6c61901d2cc72aac1b1d89d2"
        }
    sender = "eb1d2b43aad8cf60ff9911a894f80ec4f4befccc6c61901d2cc72aac1b1d89d2"
    string = string.__str__()
    sign_value = sign(string, sender)
    print(sign_value)
    """