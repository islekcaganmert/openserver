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
            db: list = json.load(f)
            if int(request.json['reminder']) < len(db):
                db[int(request.json['reminder'])]['subs'].append({
                    "deadline": request.json['deadline'],
                    "status": False,
                    "title": request.json['title']
                })
                json.dump(db, f)
    return Response(status=200)
