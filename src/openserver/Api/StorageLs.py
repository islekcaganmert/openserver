from datetime import datetime
import subprocess
import os
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied
from flask import Response


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return []
    if permissions and 'ReadFile' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Documents' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Documents")
    r = {}
    for i in os.listdir(f"./Users/{username}/Documents"):
        r.update({i: {
            "type": subprocess.check_output(f"file -b './Users/{username}/Documents/{i}'", shell=True).decode().strip(),
            "size": os.path.getsize(f"./Users/{username}/Documents/{i}"),
            "created": datetime.fromtimestamp(os.path.getctime(f"./Users/{username}/Documents/{i}")).strftime('%Y-%m-%d %H:%M'),
            "edited": datetime.fromtimestamp(os.path.getmtime(f"./Users/{username}/Documents/{i}")).strftime('%Y-%m-%d %H:%M')
        }})
    return r
