from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation
from datetime import datetime, UTC

async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if '..' in request.json['list']:
        report(DirectoryEscalation)
        return Response(status=403)
    if f'{request.json['list']}.json' in os.listdir(f'./Users/{request.json['current_user_username']}/Reminders'):
        with open(f'./Users/{request.json['current_user_username']}/Reminders/{request.json['list']}.json', 'r') as f:
            db = json.load(f)
        with open(f'./Users/{request.json['current_user_username']}/Reminders/{request.json['list']}.json', 'w') as f:
            if int(request.json['id']) < len(db):
                db[int(request.json['id'])]['status'] = not db[int(request.json['id'])]['status']
                db[int(request.json['id'])]['last_update_status'] = datetime.now(UTC).strftime('%Y-%m-%d %H:%M')
                json.dump(db, f)
    return Response(status=200)
