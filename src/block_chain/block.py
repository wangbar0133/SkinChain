import os
import time 
import json
import random

from bin.encrypt import tran_16_to_2, hash, sign
from db.mongodb import db

class Block():
    """区块对象"""
    def __init__(self, index, sender, recive, pr_block_hash, high, coin, mesg):
        self.block = {
            "header": {
                "index": index,
                "pr_block_hash": pr_block_hash,
                "high": high,
                "timestamp": str(time.time()),
                "sender": sender
            },
            "tran": {               
                "recive": recive,
                "coin": coin,
                "mesg": mesg
            },
            "sign": sign(bytes(self.block["header"].__str__() + self.block["trans_list"].__str__(), encoding='UTF-8'), encoding="base64"),       
            "block_hash": hash(self.block["header"].__str__() + self.block["trans_list"].__str__())
        }
    
    def print_block(self):
        print(self.block)
        
    def add_tran(self, trans_list):
        self.block["trans_list"].append(trans_list)
        
              
class BlockChain(db):
    
    def __init__(self):
        pass
    
    def add_block_to_blockchain(self, block):
        self.insert(block)
    
    def get_user_history(self, user):
        block_list = self.get_block_list_by_user(user)
        user_list = []
        for send_list in block_list["send"]:
            user_list.append({
                "timestamp": send_list["timestamp"],
                "recive": send_list["tran"]["recive"],
                "coin": send_list["tran"]["coin"]
            })        
            
        for recive_list in block_list["recive"]:
            user_list.append({
                "timestamp": send_list["timestamp"],
                "sender": send_list["sender"],
                "coin": send_list["tran"]["coin"]
            })
        
        return sorted(user_list, key=lambda i: i['timestamp'])

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
    
    