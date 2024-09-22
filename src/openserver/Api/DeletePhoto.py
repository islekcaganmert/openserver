from flask import Response
import subprocess
import hashlib
import json
import jwt
import os


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        return Response(status=404)
    if 'Trash' not in os.listdir(f"./Users/{username}/Pictures/"):
        return Response(status=404)
    filename: str = request.json['filename'].replace('/', '').replace('\\', '').replace('..', '')
    if 'Pictures.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/Pictures.json") as f:
            d = json.load(f)
    else:
        d = {}
    albums = []
    for i in d:
        if filename in d[i]:
            albums.append(i)
    if not filename:
        return Response(status=400)
    if filename in os.listdir(f"./Users/{username}/Pictures/"):
        os.remove(f"./Users/{username}/Pictures/{filename}")
    elif filename in os.listdir(f"./Users/{username}/Pictures/Trash/"):
        os.remove(f"./Users/{username}/Pictures/Trash/{filename}")
    else:
        return Response(status=404)
    return Response(status=200)