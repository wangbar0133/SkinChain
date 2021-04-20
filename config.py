import os


class Config:
    PORT = 9999
    SHACKPORT = 9998
    IPPOOL = "192.168.0.255"
    SECRET_KEY = "SECRETKEY"
    UPLOAD_FOLDER = os.getcwd() + "\\coins\\"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024