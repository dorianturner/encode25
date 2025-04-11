import json

d = dict()

for token in json.load(open("test.json")):
    if "platforms" in token and "ethereum" in token["platforms"]:
        addr = token["platforms"]["ethereum"]
        d[addr] = token["symbol"]

print(d)