from flask import Response
import json
import jwt
import os


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if 'Photos.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/Photos.json") as f:
            d = json.load(f)
    else:
        d = {}
    if request.json['name'] in d:
        d.pop(request.json['name'])
        with open(f"./Users/{username}/Library/Pictures.json", 'w') as f:
            json.dump(d, f)
    return Response(status=200)