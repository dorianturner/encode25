import json

d = dict()

for token in json.load(open("test.json")):
    if "platforms" in token and "ethereum" in token["platforms"]:
        addr = token["platforms"]["ethereum"]
        d[token["symbol"].upper()] = addr

print(d)