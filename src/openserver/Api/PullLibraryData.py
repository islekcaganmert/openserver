import json
import os
from flask import Response
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
from openserver.Helpers.GetLogin import get_login


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
    dir: str = f'./Users/{username}/Library/Data/'
    if app not in os.listdir(dir):
        with open(f'{dir}/{app}', 'w') as f:
            f.write('{}')
    with open(f'{dir}/{app}') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
