import os
from flask import Response
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=403)
    if permissions and 'WriteFile' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Documents' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Documents")
    folder = request.json.get('folder')
    if '/../' in ('/' + folder + '/'):
        return Response(status=403)
    folder = f"./Users/{username}/Documents/{folder}".replace('//', '/')
    os.makedirs(folder, exist_ok=True)
    return Response(status=200)
