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
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        return Response(status=404)
    if 'Trash' not in os.listdir(f"./Users/{username}/Pictures/"):
        return Response(status=404)
    filename: str = request.json['filename'].replace('/', '').replace('\\', '').replace('..', '')
    if 'Pictures.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/Pictures.json") as f:
            d = json.load(f)
    else:
        d = {}
    albums = []
    for i in d:
        if filename in d[i]:
            albums.append(i)
    if not filename:
        return Response(status=400)
    if filename in os.listdir(f"./Users/{username}/Pictures/"):
        os.remove(f"./Users/{username}/Pictures/{filename}")
    elif filename in os.listdir(f"./Users/{username}/Pictures/Trash/"):
        os.remove(f"./Users/{username}/Pictures/Trash/{filename}")
    else:
        return Response(status=404)
    return Response(status=200)
