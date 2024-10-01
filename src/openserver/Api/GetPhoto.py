from flask import Response
import subprocess
import hashlib
import json
from openserver.Helpers.Report import report, PermissionDenied
import os
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'PhotosRead' not in permissions:
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
        with open(f"./Users/{username}/Pictures/{filename}", 'rb') as f:
            content: bytes = f.read()
    elif filename in os.listdir(f"./Users/{username}/Pictures/Trash/"):
        with open(f"./Users/{username}/Pictures/Trash/{filename}", 'rb') as f:
            content: bytes = f.read()
    else:
        return Response(status=404)
    return {
        "filetype": subprocess.run(['file', '-b', f"./Users/{username}/Pictures/{filename}"], capture_output=True).stdout.decode().strip('\n'),
        "hex": content.hex(),
        "hash": hashlib.sha512(content).hexdigest(),
        "albums": albums,
        "date": f"{filename[:4]}-{filename[4:6]}-{filename[6:8]} {filename[8:10]}:{filename[10:12]}:{filename[12:14]}"
    }
