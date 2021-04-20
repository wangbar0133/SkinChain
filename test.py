import socket
import time
import json
import ed25519
import os
from config import Config


if __name__ == "__main__":
    path = "C:\\Users\\Administrator.DESKTOP-35V3OQH\\.vscode"
    pic_path_dict = os.listdir(path)
    pic_path = path + pic_path_dict[0]
    print(pic_path)