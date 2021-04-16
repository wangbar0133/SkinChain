import os
import json
import ed25519

from ..block_chain.block import BlockChain, Block
from ..p2p.udp import push_block


class Account():
    """用户对象"""
    def __init__(self):
        self.signing_key, self.verifying_key = ed25519.create_keypair()
        self.PublicKey = self.verifying_key.to_ascii(encoding="hex")
        self.PrivateKey = self.signing_key.to_ascii(encoding="hex")
        self.SigningKey = self.signing_key
        self.VerifiyingKey = self.verifying_key
        self.Username = str(self.PublicKey)[2:-1]
        self.Password = str(self.PrivateKey)[2:-1]
    

class AccountOpertion(BlockChain):
    """用户操作对象"""
    def __init__(self, user):
        BlockChain.__init__(self)
        self.user_history = self.get_user_history(user)
        self.user = user

    def show_coins(self):
        """展示一个用户的所有资产"""
        coin_dict = {}
        for history in self.user_history:
            coin = history["coin"]
            if "recive" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1
            elif "sender" in history.keys():
                try:
                    coin_dict[coin] = coin_dict[coin] - 1
                except:
                    print("err")
            elif "creater" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1

        coin_list = []
        for coin in coin_dict:
            if coin_dict[coin] == 1:
                coin_list.append(coin)
        return coin_list
    
    def show_trans_history(self):
        """查看用户的历史纪录"""
        return self.get_user_history(self.user)

    def show_create(self):
        """查看用户作品"""
        coin_dict = {}
        for history in self.user_history:
            coin = history["coin"]
            if "creater" in history.keys():
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1
        coin_list = []
        for coin in coin_dict:
            if coin_dict[coin] == 1:
                coin_list.append(coin)
        return coin_list

    def send_coin(self, recive, coin, mesg):
        """向别人交易"""
        index = BlockChain().get_top_block_index() + 1
        sender = self.user
        pr_block_hash = BlockChain().get_top_block_hash()
        block = Block(index, sender, recive, pr_block_hash, coin, mesg)
        for count in range(10):
            if BlockChain().insert_block(block):
                break
        ip_list_su = push_block(block)
        return ip_list_su
