import time

from src.bin.mongodb import Db


class BlockChain(Db):

    def insert_block(self, block):
        return self.insert(block)

    def get_user_history(self, user):
        block_list = self.get_block_list_by_user(user)
        if not block_list:
            return False
        # print(block_list)
        user_history_list = []
        for block in block_list:
            if block["header"]["sender"] == user and block["tran"]["recive"] != user:
                user_history_list.append({
                    "opt": "send",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "recive": block["tran"]["recive"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["tran"]["recive"] == user and block["header"]["sender"] != user:
                user_history_list.append({
                    "opt": "recive",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "sender": block["header"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
            elif block["tran"]["recive"] == user and block["header"]["sender"] == user:
                user_history_list.append({
                    "opt": "create",
                    "timestamp": int(float(block["header"]["timestamp"])),
                    "creater": block["header"]["sender"],
                    "coin": block["tran"]["coin"],
                    "mesg": block["tran"]["mesg"]
                })
        user_history_list = sorted(user_history_list, key=lambda i: i['timestamp'])
        for index, coin in enumerate(user_history_list):
            user_history_list[index]["timestamp"] = time.asctime(time.localtime(int(float(coin["timestamp"]))))
        return user_history_list

    def get_coin_history(self, coin):
        block_list = self.get_block_list_by_coin(coin)
        if not block_list:
            return False
        coin_list = []
        for block in block_list:
            coin_list.append({
                "timestamp": block["header"]["timestamp"],
                "sender": block["header"]["sender"],
                "recive": block["tran"]["recive"],
                "mesg": block["tran"]["mesg"]
            })
        coin_list = sorted(coin_list, key=lambda i: i['timestamp'])
        for index, coin in enumerate(coin_list):
            coin_list[index]["timestamp"] = time.asctime(time.localtime(int(float(coin["timestamp"]))))
        return coin_list

    def get_top_block_index(self):
        top_block = self.get_top_block()
        return int(top_block["header"]["index"])

    def get_top_block_hash(self):
        top_block = self.get_top_block()
        return top_block["block_hash"]


if __name__ == "__main__":
    print(BlockChain().get_user_history("2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6"))
