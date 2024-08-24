import json
import os

import jwt
from flask import Response
from openserver.Helpers.Report import report, DirectoryEscalation


# noinspection PyShadowingBuiltins
async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return {}
    if '/' in request.json['app']:
        report(DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    dir: str = f'./Users/{username}/Library/Data/'
    if app not in os.listdir(dir):
        with open(f'{dir}/{app}', 'w') as f:
            f.write('{}')
    with open(f'{dir}/{app}') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
