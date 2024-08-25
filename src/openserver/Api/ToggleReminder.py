import jwt
from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation
from datetime import datetime, UTC


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
        with open(f'./Users/{username}/Reminders/{request.json['list']}.json', 'w') as f:
            if '/' in request.json['id']:
                if int(request.json['id'].split('/')[0]) < len(db):
                    if int(request.json['id'].split('/')[1]) < len(db[int(request.json['id'].split('/')[0])]):
                        db[int(request.json['id'].split('/')[0])]['subs'][int(request.json['id'].split('/')[1])]['status'] = not db[int(request.json['id'].split('/')[0])]['subs'][int(request.json['id'].split('/')[1])]['status']
                        json.dump(db, f)
            else:
                if int(request.json['id']) < len(db):
                    db[int(request.json['id'])]['status'] = not db[int(request.json['id'])]['status']
                    db[int(request.json['id'])]['last_update_status'] = datetime.now(UTC).strftime('%Y-%m-%d %H:%M')
                    json.dump(db, f)
    return Response(status=200)
