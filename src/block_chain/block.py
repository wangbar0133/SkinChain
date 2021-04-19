import os
import time 
import json
import random
import traceback

from src.bin.encrypt import hash_sha256, sign, check_sign, check_hash
from src.db.mongodb import Db



class Block(object):
    """区块对象"""
    def __init__(self, index, sender, recive, pr_block_hash, coin, mesg):
        self.block = {
            "header": {
                "index": index,
                "pr_block_hash": pr_block_hash,
                "timestamp": str(time.time()),
                "sender": sender
            },
            "tran": {               
                "recive": recive,
                "coin": coin,
                "mesg": mesg
            },
            "sign": sign(bytes(self.block["header"].__str__() + self.block["trans_list"].__str__(), encoding='UTF-8')),
            "block_hash": hash_sha256(self.block["header"].__str__() + self.block["trans_list"].__str__())
        }
    
    def print_block(self):
        print(self.block)
        
    def add_tran(self, trans_list):
        self.block["trans_list"].append(trans_list)
        
              
class BlockChain(Db):

    def insert_block(self, block):
        try:
            self.insert(block)
            result = True
        except:
            traceback.print_exc()
            result = False
        return result

    def add_block_to_blockchain(self, block):
        self.insert(block)
    
    def get_user_history(self, user):
        block_list = self.get_block_list_by_user(user)
        user_history_list = []
        for block in block_list:
            if block["header"]["sender"] == user and block["tran"]["recive"] != user:
                user_history_list.append({
                    "timestamp": block["timestamp"],
                    "recive": block["tran"]["recive"],
                    "coin": block["tran"]["coin"]
                })
            elif block["header"]["recive"] == user and block["tran"]["sender"] != user:
                user_history_list.append({
                    "timestamp": block["timestamp"],
                    "sender": block["tran"]["sender"],
                    "coin": block["tran"]["coin"]
                })
            elif block["header"]["recive"] == user and block["tran"]["sender"] == user:
                user_history_list.append({
                    "timestamp": block["timestamp"],
                    "creater": block["tran"]["sender"],
                    "coin": block["tran"]["coin"]
                })
        return sorted(user_history_list, key=lambda i: i['timestamp'])

    def get_coin_history(self, coin):
        block_list = self.get_block_list_by_coin(coin)
        coin_list = []
        for block in block_list:
            coin_list.append({
                "timestamp": block["timestamp"],
                "sender": block["sender"],
                "recive": block["recive"]
            })

        return sorted(coin_list, key=lambda i: i['timestamp'])

    def get_top_block_index(self):
        top_block = self.get_top_block()
        return int(top_block["headers"]["index"])

    def get_top_block_hash(self):
        top_block = self.get_top_block()
        return int(top_block["headers"]["block_hash"])




def check_block(block):
    """检查收到的块"""
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
    except:
        result = False
    finally:
        return result
