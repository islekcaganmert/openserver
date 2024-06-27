from flask import Response
import json
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if '/' in request.json['app']:
        report(DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    dir: str = f'./Users/{request.json['current_user_username']}/Library/Data/'
    data: dict = json.loads(request.json['data'])
    with open(f'{dir}/{app}', 'w') as f:
        json.dump(data, f)
    return Response(status=200)
