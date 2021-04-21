import socket
import time
import json
import ed25519
import os
from config import Config


if __name__ == "__main__":
    list_test = []
    for index in range(10):
        list_test.append({
            "value": index
        })

    for index, value in enumerate(list_test):
        list_test[index]["value"] = str(value["value"])

    print(list_test)