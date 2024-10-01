import os
from openserver.Helpers.GetLogin import get_login
from flask import Response
from openserver.Helpers.Report import report, PermissionDenied


async def main(config, request) -> (list, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'PhotosRead' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Pictures/")
    if 'Trash' not in os.listdir(f"./Users/{username}/Pictures/"):
        os.mkdir(f"./Users/{username}/Pictures/Trash/")
    return list(sorted(os.listdir(f"./Users/{username}/Pictures/Trash/")))
