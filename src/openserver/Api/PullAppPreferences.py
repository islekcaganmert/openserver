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
    pieces = app.split('.')
    pieces.reverse()
    domain = '.'.join(pieces)
    dir: str = f'./Users/{username}/Library/Preferences/'
    if 'Preferences' not in os.listdir(f'./Users/{username}/Library'):
        os.mkdir(f'./Users/{username}/Library/Preferences')
    if app not in os.listdir(dir):
        with open(f'{dir}/{app}', 'w') as f:
            resp = requests.get(f'https://{domain}/.well-known/app_info.json')
            if resp.status_code == 200:
                defaults = resp.json()['preferences']
                json.dump(defaults, f)
            else:
                f.write('{}')
    with open(f'{dir}{app}') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
