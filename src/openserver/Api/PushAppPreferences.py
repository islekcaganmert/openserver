import os
import jwt
from flask import Response
import json
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if '/' in request.json['app']:
        report(DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    # noinspection PyShadowingBuiltins
    dir: str = f'./Users/{username}/Library/Preferences/'
    if 'Preferences' not in os.listdir(f'./Users/{username}/Library'):
        os.mkdir(f'./Users/{username}/Library/Preferences')
    data: dict = json.loads(request.json['data']) if isinstance(request.json['data'], str) else request.json['data']
    with open(f'{dir}/{app}', 'w') as f:
        json.dump(data, f)
    return Response(status=200)
