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
            
    def insert(self, block):
        self.mycol.insert_one(block)
    
    def get_top_block(self):
        block = self.mycol.find().sort('_id', -1).limit(1)
        return json_util.dumps(block)

    def get_chain_len(self):
        return self.mycol.count()
    
    def get_block_by_index(self, index):
        return json_util.dumps(self.mycol.find({}, {"index": index}))

    def get_block_list_by_user(self, user):
        return set(json_util.dumps(self.mycol.find({}, {"header.sender": user}))
                   + json_util.dumps(self.mycol.find({}, {"tran.recive": user})))

    def get_block_list_by_coin(self, coin):
        return json_util.dumps(self.mycol.find({}, {"tran.coin": coin}))
