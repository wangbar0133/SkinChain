import os
import json
import ed25519

from block_chain.block import BlockChain

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
        self.user_history = self.get_user_history(user)
           
    def show_coins(self):
        coin_dict = {}
        for tran in user_history:
            coin = tran["coin"]
            if coin_dict.has_key("recive"):
                coin_dict[coin] = coin_dict[coin] + 1 if coin in coin_dict else 1
            elif coin_dict.has_key("recive"):
                try:
                    coin_dict[coin] = coin_dict[coin] - 1
                except:
                    print("err")
        coin_list = []
        for coin in coin_dict:
            if coin_dict[coin] != 0:
                coin_list.append(coin)
                
        return coin_list
    
    def show_trans_history(self):
        return self.get_user_history(self.user)
    
    def send_coin(self, recive, coin, mesg):
        pass