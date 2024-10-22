from datetime import datetime, UTC
from flask import Response
import hashlib
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
    now = datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')
    extension = request.json['filename'].split(' ')[0]
    filename: str = f"{now}.{extension}"
    content: bytes = bytes.fromhex(request.json['hex'])
    if hashlib.sha512(content).hexdigest() != request.json['hash']:
        return Response(status=400)
    with open(f"./Users/{username}/Pictures/{filename}", 'wb') as f:
        f.write(content)
    return Response(status=200)
