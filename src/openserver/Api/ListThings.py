import json
import jwt
import os


async def main(config, request) -> list[str]:
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return []
    if 'IoT.json' not in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/IoT.json", "w") as f:
            f.write('{"things": {}, "rooms": []}')
    with open(f"./Users/{username}/Library/IoT.json") as f:
        d = json.load(f)
        r = []
        for i in d['things']:
            if d['things'][i]['room'] == request.json['room']:
                r.append(i)
        return r
