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
        create = {}
        for block in block_list:
            if block["header"]["sender"] == block["tran"]["recive"]:
                create = {
                    "detial": time.asctime(time.localtime(int(float(block["header"]["timestamp"]))))
                              + "创建于用户：" + block["header"]["sender"],
                    "mesg": block["tran"]["mesg"]
                }
            else:
                coin_list.append({
                    "timestamp": block["header"]["timestamp"],
                    "sender": block["header"]["sender"],
                    "recive": block["tran"]["recive"],
                    "mesg": block["tran"]["mesg"]
                })
        coin_list = sorted(coin_list, key=lambda i: i['timestamp'])
        for index, coin in enumerate(coin_list):
            coin_list[index]["timestamp"] = time.asctime(time.localtime(int(float(coin["timestamp"]))))
        return create, coin_list

    def get_top_block_index(self):
        top_block = self.get_top_block()
        return int(top_block["header"]["index"])

    def get_top_block_hash(self):
        top_block = self.get_top_block()
        return top_block["block_hash"]

    def get_all_coins(self):
        block_list = self.get_chain()
        coin_list = list()
        for block in block_list:
            if block["header"]["sender"] == block["tran"]["recive"]:
                coin = block["tran"]["coin"]
                coin_list.append(coin)
        return coin_list

    def get_block_by_user_coin(self, user, coin):
        chain = self.get_chain()
        history = list()
        for block in chain:
            if (block["header"]["sender"] == user or block["tran"]["recive"] == user) and block["tran"]["coin"] == coin:
                history.append({
                    "timestamp": block["header"]["timestamp"],
                    "coin": block["tran"]["coin"],
                    "sender": block["header"]["sender"],
                    "recive": block["tran"]["recive"],
                    "mesg": block["tran"]["mesg"]
                })
        return history

    def get_history(self):
        chain = self.get_chain()
        history = list()
        for block in chain:
            history.append({
                "timestamp": time.asctime(time.localtime(int(float(block["header"]["timestamp"])))),
                "coin": block["tran"]["coin"],
                "img_url": "/display/img/" + block["tran"]["coin"],
                "sender": block["header"]["sender"],
                "recive": block["tran"]["recive"],
                "mesg": block["tran"]["mesg"]
            })
        return history


if __name__ == "__main__":
    user = "2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6"
    coin = "fc503153dab068850d83a3e7dbb88585"
    chain = BlockChain()
    print(chain.get_history())
    pass
