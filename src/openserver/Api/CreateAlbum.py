from flask import Response
import json
import os
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'PhotosModify' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Pictures.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/Pictures.json") as f:
            d = json.load(f)
    else:
        d = {}
    if request.json['name'] not in d:
        d[request.json['name']] = []
        with open(f"./Users/{username}/Library/Pictures.json", 'w') as f:
            json.dump(d, f)
    return Response(status=200)
