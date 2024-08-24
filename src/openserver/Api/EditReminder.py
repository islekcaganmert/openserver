import jwt
from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if '..' in request.json['list']:
        report(DirectoryEscalation)
        return Response(status=403)
    if f'{request.json['list']}.json' in os.listdir(f'./Users/{username}/Reminders'):
        with open(f'./Users/{username}/Reminders/{request.json['list']}.json') as f:
            db = json.load(f)
            if int(request.json['id']) < len(db):
                db[int(request.json['id'])] = json.loads(request.json['data']) if isinstance(request.json['data'], str) else request.json['data']
                json.dump(db, f)
    return Response(status=200)
