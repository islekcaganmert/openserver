import jwt
import os

from flask import Response


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=403)
    if 'Documents' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Documents")
    folder = request.json.get('folder')
    if '/../' in ('/' + folder + '/'):
        return Response(status=403)
    folder = f"./Users/{username}/Documents/{folder}".replace('//', '/')
    os.makedirs(folder, exist_ok=True)
    return Response(status=200)
