# -*-coding:utf-8-*-
import json

import pymongo
from bson import json_util

from src.bin.log import Log


class Db(object):
    
    def __init__(self):
        try:
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            dblist = myclient.list_database_names()
            if "skin_chain" not in dblist:
                Log().info("数据库不存在，正在创建--------")
                print("数据库不存在，正在创建--------")
                mydb = myclient["skin_chain"]
                Log().info("已创建skin_chain数据库")
                print("已创建skin_chain数据库")
            else:
                mydb = myclient["skin_chain"]
            self.mycol = mydb["chain"]
        except Exception as e:
            print("数据库创建失败：" + str(e))
            Log().error("数据库创建失败：" + str(e))

    def test(self, user):
        block_list = json_util.dumps(self.mycol.find({"header.sender": user}, {"_id": False}))
        return block_list

    def insert(self, block):
        """在数据库插入新的块"""
        try:
            self.mycol.insert_one(block.block_dict)
            return True
        except Exception as e:
            Log().error("区块插入失败：" + str(e))
            print(e)
            return False

    def insert_dict(self, block):
        self.mycol.insert_one(block)

    def delete(self, index):
        """根据索引删除块"""
        try:
            self.mycol.delete_one({"header.index": index})
        except Exception as e:
            Log().error("删除失败：" + str(e))

    def clean(self):
        """清空数据库"""
        try:
            self.mycol.delete_many({})
        except Exception as e:
            Log().error("清空数据库失败：" + str(e))

    def get_top_block(self):
        """获取最新的块"""
        block = self.mycol.find({}, {"_id": False}).sort("_id", -1).limit(1)
        return json.loads(json_util.dumps(block))[0]

    def get_chain_len(self):
        """获取链的长度"""
        return self.mycol.count()
    
    def get_block_by_index(self, index):
        """通过索引获取最新的块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({"header.index": index}, {"_id": False})))[0]
        except Exception as e:
            Log().error("获取最新块失败：" + str(e))

    def get_block_list_by_user(self, user):
        """获取含有某一用户的所有块"""
        try:
            block_list_raw = json.loads(json_util.dumps(self.mycol.find({"header.sender": user}, {"_id": False}))) \
                             + json.loads(json_util.dumps(self.mycol.find({"tran.recive": user}, {"_id": False})))
            block_list = []
            for item in block_list_raw:
                if item not in block_list:
                    block_list.append(item)
            return block_list
        except Exception as e:
            Log().error("通过用户获取块失败：" + str(e))

    def get_block_list_by_coin(self, coin):
        """获取含有某一资产的所有块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({"tran.coin": coin}, {"_id": False})))
        except Exception as e:
            Log().error("通过资产获取块失败：" + str(e))


if __name__ == "__main__":

    block = {
                "header": {
                    "index": 0,
                    "pr_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                    "timestamp": "1619527476.338443",
                    "sender": "2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6"
                },
                "tran": {
                    "recive": "2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6",
                    "coin": "fc503153dab068850d83a3e7dbb88585",
                    "mesg": "Genesis_Block"
                },
                "sign": "A0Y8qcIfYB8AVEKb7F7WbuMOSTEN+pYnCJ9rvfOiwhFNwQ3Fufk0J+EbZ8jDSak1XkN1UxSTsA1KK/wZN7JVCg",
                "block_hash": "d089af7383e1291a8863504ede230a5bbb701df42f948eb10540ab266d889ea6"
            }
    # block = json.loads(block.__str__().replace("'", '"'))
    # print(type(block))
    # Db().insert_dict(block)
    print(Db().get_block_list_by_user("2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6"))
    pass
