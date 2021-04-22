import time


from src.bin.mongodb import Db


class BlockChain(Db):

    def insert_block(self, block):
        return self.insert(block)

    def get_user_history(self, user):
        block_list = self.get_block_list_by_user(user)
        if not block_list:
            return False
        user_history_list = []
        for block in block_list:
            if block["header"]["sender"] == user and block["tran"]["recive"] != user:
                user_history_list.append({
                    "opt": "send",
                    "timestamp": time.asctime(time.localtime(block["timestamp"])),
                    "recive": block["tran"]["recive"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["header"]["recive"] == user and block["tran"]["sender"] != user:
                user_history_list.append({
                    "opt": "recive",
                    "timestamp": time.asctime(time.localtime(block["timestamp"])),
                    "sender": block["tran"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["header"]["recive"] == user and block["tran"]["sender"] == user:
                user_history_list.append({
                    "opt": "create",
                    "timestamp": time.asctime(time.localtime(block["timestamp"])),
                    "creater": block["tran"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            user_history_list = sorted(user_history_list, key=lambda i: i['timestamp'])
            for index, coin in enumerate(user_history_list):
                user_history_list[index]["timestamp"] = time.asctime(time.localtime(coin["timestamp"]))
        return user_history_list



    def get_coin_history(self, coin):
        block_list = self.get_block_list_by_coin(coin)
        if not block_list:
            return False
        coin_list = []
        for block in block_list:
            coin_list.append({
                "timestamp": block["timestamp"],
                "sender": block["sender"],
                "recive": block["tran"]["recive"],
                "mesg": block["tran"]["mesg"]
            })
        coin_list = sorted(coin_list, key=lambda i: i['timestamp'])
        for index, value in enumerate(coin_list):
            coin_list[index]["timestamp"] = time.asctime(time.localtime(coin["timestamp"]))
        return coin_list

    def get_top_block_index(self):
        top_block = self.get_top_block()
        return int(top_block["headers"]["index"])

    def get_top_block_hash(self):
        top_block = self.get_top_block()
        return int(top_block["headers"]["block_hash"])