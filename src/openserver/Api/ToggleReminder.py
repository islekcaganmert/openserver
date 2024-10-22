from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
from datetime import datetime, UTC
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'RemindersWrite' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if '..' in request.json['list']:
        report(config, DirectoryEscalation)
        return Response(status=403)
    if f"{request.json['list']}.json" in os.listdir(f'./Users/{username}/Reminders'):
        with open(f"./Users/{username}/Reminders/{request.json['list']}.json") as f:
            db = json.load(f)
        with open(f"./Users/{username}/Reminders/{request.json['list']}.json", 'w') as f:
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
