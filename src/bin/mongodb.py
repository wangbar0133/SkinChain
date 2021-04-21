import os
import json
import pymongo
import traceback
from bson import json_util


class Db(object):
    
    def __init__(self):
        try:
            myclient = pymongo.MongoClient('mongodb://localhost:27017/')
            dblist = myclient.list_database_names()
            if "skin_chain" not in dblist:
                print("数据库不存在，正在创建--------")
                mydb = myclient["skin_chain"]
                print("已创建skin_chain数据库")
            self.mycol = mydb["chain"]
        except:
            traceback.print_exc()

    def test(self, obj):
        self.mycol.insert_one(obj)

    def insert(self, block):
        """在数据库插入新的块"""
        self.mycol.insert_one(block)

    def delete(self, index):
        """根据索引删除块"""
        self.mycol.delete_one({"header.index": index})

    def clean(self):
        """清空数据库"""
        self.mycol.delete_many({})

    def get_top_block(self):
        """获取最新的块"""
        block = self.mycol.find().sort('_id', -1).limit(1)
        return json_util.dumps(block)

    def get_chain_len(self):
        """获取链的长度"""
        return self.mycol.count()
    
    def get_block_by_index(self, index):
        """通过索引获取最新的块"""
        return json_util.dumps(self.mycol.find({}, {"header.index": index}))

    def get_block_list_by_user(self, user):
        """获取含有某一用户的所有块"""
        return set(json_util.dumps(self.mycol.find({}, {"header.sender": user}))
                   + json_util.dumps(self.mycol.find({}, {"tran.recive": user})))

    def get_block_list_by_coin(self, coin):
        """获取含有某一资产的所有块"""
        return json_util.dumps(self.mycol.find({}, {"tran.coin": coin}))


# if __name__ == "__main__":
