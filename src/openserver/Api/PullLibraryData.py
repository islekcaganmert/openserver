import json
import os
from flask import Response
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request) -> dict:
    if request.json['current_user_username'] == 'Guest':
        return {}
    if '/' in request.json['app']:
        report(DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    dir: str = f'./Users/{request.json['current_user_username']}/Library/Data/'
    if app not in os.listdir(dir):
        with open(f'{dir}/{app}', 'w') as f:
            f.write('{}')
    with open(f'{dir}/{app}', 'r') as f:
        try:
            return json.load(f)
        except:
            return {}
