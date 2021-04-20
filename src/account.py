import os
import json
import time
import ed25519

from block import BlockChain, Block
from udp import Client


class Account(object):
    """用户对象"""
    def __init__(self):
        self.signing_key, self.verifying_key = ed25519.create_keypair()
        self.PublicKey = self.verifying_key.to_ascii(encoding="hex")
        self.PrivateKey = self.signing_key.to_ascii(encoding="hex")
        self.SigningKey = self.signing_key
        self.VerifiyingKey = self.verifying_key
        self.Username = str(self.PublicKey)[2:-1]
        self.Password = str(self.PrivateKey)[2:-1]

    def create_account(self):
        return self.Username, self.Password


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

    def show_coin_count(self):
        return len(self.show_coins())

    def show_trans_history(self):
        """查看用户的历史纪录"""
        history_list = self.get_user_history(self.user)
        user_history = []
        for history in history_list:
            if history["opt"] == "send":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "发送给" + history["recive"]
                })
            elif history["opt"] == "recive":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "收到从" + history["recive"]
                })
            elif history["opt"] == "create":
                user_history.append({
                    "timestamp": time.asctime(time.localtime(history["timestamp"])),
                    "coin": history["coin"],
                    "desc": "创建"
                })
        return user_history

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
        Client().sync_chain(index=index - 1)
        block = Block(index, sender, recive, pr_block_hash, coin, mesg)
        if BlockChain().insert_block(block):
            Client().push_blocks([block])
        return index

    def create_coin(self, coin, mesg=None):
        """上传作品"""
        index = BlockChain().get_top_block_index() + 1
        sender = self.user
        recive = self.user
        pr_block_hash = BlockChain().get_top_block_hash()
        Client().sync_chain(index=index - 1)
        block = Block(index, sender, recive, pr_block_hash, coin, mesg)
        if BlockChain().insert_block(block):
            Client().push_blocks([block])
        return index


def check_block(block):
    """检查收到的块"""
    from encrypt import check_sign, check_hash
    result = True
    try:
        string = block["header"].__str__() + block["trans_list"].__str__()
        sig = block["sign"]
        user_name = block["header"]["sender"]
        hash_value = block["block_hash"]
        if not check_sign(string, sig, user_name):
            result = False
        if not check_hash(string, hash_value):
            result = False
        block_index = int(block["header"]["index"])
        db_top_index = BlockChain().get_top_block_index()
        if block_index != db_top_index + 1:
            result = False
        if block["header"]["pr_block_hash"] != BlockChain().get_top_block_hash():
            result = False
        sender = block["header"]["sender"]
        coin = block["tran"]["coin"]
        sender_obj = AccountOpertion(sender)
        coin_list = sender_obj.show_coins()
        if coin in coin_list:
            return False
    except:
        result = False
    finally:
        return result
