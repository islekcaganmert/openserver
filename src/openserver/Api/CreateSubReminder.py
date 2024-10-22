from flask import Response
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
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
        with open(f"./Users/{username}/Reminders/{request.json['list']}.json") as fr:
            db: list = json.load(fr)
        with open(f"./Users/{username}/Reminders/{request.json['list']}.json", 'w') as fw:
            if int(request.json['reminder']) < len(db):
                db[int(request.json['reminder'])]['subs'].append({
                    "deadline": request.json['deadline'],
                    "status": False,
                    "title": request.json['title']
                })
                json.dump(db, fw)
    return Response(status=200)
