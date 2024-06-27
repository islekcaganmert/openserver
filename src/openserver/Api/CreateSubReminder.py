from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if '..' in request.json['list']:
        report(DirectoryEscalation)
        return Response(status=403)
    if f'{request.json['list']}.json' in os.listdir(f'./Users/{request.json['current_user_username']}/Reminders'):
        with open(f'./Users/{request.json['current_user_username']}/Reminders/{request.json['list']}.json') as f:
            db: list = json.load(f)
            if int(request.json['reminder']) < len(db):
                db[int(request.json['reminder'])]['subs'].append({
                    "deadline": request.json['deadline'],
                    "status": False,
                    "title": request.json['title']
                })
                json.dump(db, f)
    return Response(status=200)
