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
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Pictures/")
    if 'Trash' not in os.listdir(f"./Users/{username}/Pictures/"):
        os.mkdir(f"./Users/{username}/Pictures/Trash/")
    filename: str = request.json['filename'].replace('/', '').replace('\\', '').replace('..', '')
    if not filename:
        return Response(status=400)
    if filename in os.listdir(f"./Users/{username}/Pictures/"):
        os.rename(f"./Users/{username}/Pictures/{filename}", f"./Users/{username}/Pictures/Trash/{filename}")
    elif filename in os.listdir(f"./Users/{username}/Pictures/Trash/"):
        os.rename(f"./Users/{username}/Pictures/Trash/{filename}", f"./Users/{username}/Pictures/{filename}")
    return Response(status=200)
