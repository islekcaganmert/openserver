from flask import Response
import os
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
    path = request.json.get('path')
    if '/../' in ('/' + path + '/'):
        return Response(status=403)
    path = f"./Users/{username}/Documents/{path}".replace('//', '/').replace("'", "")
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.system(f"rm -rf '{path}'")
    return Response(status=200)
