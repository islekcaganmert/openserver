import json
import os
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied
from flask import Response


async def main(config, request) -> (list[str], Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return []
    if permissions and ('IoT-Full' not in permissions or 'IoT' not in permissions):
        report(config, PermissionDenied)
        return Response(status=403)
    if 'IoT.json' not in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/IoT.json", "w") as f:
            f.write('{"things": {}, "rooms": []}')
    with open(f"./Users/{username}/Library/IoT.json") as f:
        d = json.load(f)
        return d['rooms']
