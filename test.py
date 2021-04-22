import socket
import time
import json
import ed25519
import os
from config import Config
import pymongo


if __name__ == "__main__":
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')

    mydb = myclient["skinchain"]


