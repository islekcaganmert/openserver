from flask import Response
import json
import jwt
import os


async def main(config, request) -> Response:
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if 'IoT.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/IoT.json") as f:
            d = json.load(f)
    else:
        d = {}
    if request.json['name'] not in d['rooms']:
        d['rooms'].append(request.json['name'])
    with open(f"./Users/{username}/Library/IoT.json", "w") as f:
        f.write(json.dumps(d))
    return Response(status=200)
