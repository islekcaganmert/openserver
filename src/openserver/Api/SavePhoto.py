from datetime import datetime, UTC
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
    now = datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')
    extension = request.json['filename'].split(' ')[0]
    filename: str = f"{now}.{extension}"
    content: bytes = bytes.fromhex(request.json['hex'])
    if hashlib.sha512(content).hexdigest() != request.json['hash']:
        return Response(status=400)
    with open(f"./Users/{username}/Pictures/{filename}", 'wb') as f:
        f.write(content)
    return Response(status=200)