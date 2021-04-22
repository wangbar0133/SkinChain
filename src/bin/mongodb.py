# -*-coding:utf-8-*-
import os
import json
import pymongo

from bson import json_util
from src.bin.log import Log


class Db(object):
    
    def __init__(self):
        try:
            myclient = pymongo.MongoClient('mongodb://localhost:27017/')
            dblist = myclient.list_database_names()
            if "skin_chain" not in dblist:
                Log().info("数据库不存在，正在创建--------")
                print("数据库不存在，正在创建--------")
                mydb = myclient["skin_chain"]
                Log().info("已创建skin_chain数据库")
                print("已创建skin_chain数据库")
            self.mycol = mydb["chain"]
        except Exception as e:
            print("数据库创建失败：" + str(e))
            Log().error("数据库创建失败：" + str(e))

    def test(self, obj):
        self.mycol.insert_one(obj)

    def insert(self, block):
        """在数据库插入新的块"""
        try:
            self.mycol.insert_one(block)
            return True
        except Exception as e:
            Log().error("区块插入失败：" + str(e))
            return False

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
        block = self.mycol.find().sort('_id', -1).limit(1)
        return json.loads(json_util.dumps(block))

    def get_chain_len(self):
        """获取链的长度"""
        return self.mycol.count()
    
    def get_block_by_index(self, index):
        """通过索引获取最新的块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({}, {"header.index": index})))
        except Exception as e:
            Log().error("获取最新块失败：" + str(e))

    def get_block_list_by_user(self, user):
        """获取含有某一用户的所有块"""
        try:
            return list(set(json.loads(json_util.dumps(self.mycol.find({}, {"header.sender": user})))
                            + json.loads(json_util.dumps(self.mycol.find({}, {"tran.recive": user})))))
        except Exception as e:
            Log().error("通过用户获取块失败：" + str(e))

    def get_block_list_by_coin(self, coin):
        """获取含有某一资产的所有块"""
        try:
            return json.loads(json_util.dumps(self.mycol.find({}, {"tran.coin": coin})))
        except Exception as e:
            Log().error("通过资产获取块失败：" + str(e))


if __name__ == "__main__":
    user = "2b3f734685ff089104fa1cbb02cb8ceae723fcfb5b9fed9fd00d09c3d11a0ce6"
    print(Db().get_block_list_by_user(user))
    # print(type(json.loads(json_util.dumps(Db().mycol.find({}, {"header.sender": user})))))

    pass
