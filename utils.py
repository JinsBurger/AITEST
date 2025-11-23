import json

def get_api_key(name):
    with open("./config.json", "r") as f:
        keys = json.load(f)["Keys"]
        return keys[name]