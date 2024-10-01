from datetime import datetime, UTC
from flask import Response
import json
import os
from openserver.Helpers.Report import report, PermissionDenied, DirectoryEscalation
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
            db: list = json.load(f)
            db.append({
                "deadline": request.json['deadline'],
                "last_update_status": datetime.now(UTC).strftime('%Y-%m-%d %H:%M'),
                "repeat": request.json['repeat'],
                "status": False,
                "subs": [],
                "title": request.json['title']
            })
        with open(f"./Users/{username}/Reminders/{request.json['list']}.json", 'w') as f:
            json.dump(db, f)
    return Response(status=200)
