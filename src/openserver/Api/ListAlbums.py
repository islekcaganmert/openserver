import json
from flask import Response
from openserver.Helpers.Report import report, PermissionDenied
import os
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (list, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'PhotosRead' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Pictures.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/Pictures.json") as f:
            d = json.load(f)
    else:
        d = {}
    return list(d.keys())
