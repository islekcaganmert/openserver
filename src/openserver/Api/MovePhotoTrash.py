from flask import Response
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
        os.mkdir(f"./Users/{username}/Pictures/")
    if 'Trash' not in os.listdir(f"./Users/{username}/Pictures/"):
        os.mkdir(f"./Users/{username}/Pictures/Trash/")
    filename: str = request.json['filename'].replace('/', '').replace('\\', '').replace('..', '')
    if not filename:
        return Response(status=400)
    if filename in os.listdir(f"./Users/{username}/Pictures/"):
        os.rename(f"./Users/{username}/Pictures/{filename}", f"./Users/{username}/Pictures/Trash/{filename}")
    elif filename in os.listdir(f"./Users/{username}/Pictures/Trash/"):
        os.rename(f"./Users/{username}/Pictures/Trash/{filename}", f"./Users/{username}/Pictures/{filename}")
    return Response(status=200)
