from flask import Response
import jwt
import os


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=403)
    if 'Documents' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Documents")
    path = request.json.get('path')
    if '/../' in ('/' + path + '/'):
        return Response(status=403)
    path = f"./Users/{username}/Documents/{path}".replace('//', '/').replace("'", "")
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.system(f"rm -rf '{path}'")
    return Response(status=200)
