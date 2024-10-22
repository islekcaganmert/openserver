import json
import os
from flask import Response
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
from openserver.Helpers.GetLogin import get_login
import requests


# noinspection PyShadowingBuiltins
async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return {}
    if '/' in request.json['app']:
        report(config, DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    if permissions and app != package_name and 'InterApp' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
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
