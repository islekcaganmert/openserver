from flask import Response
import json
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if '/' in request.json['app']:
        report(config, DirectoryEscalation)
        return Response(status=403)
    app: str = request.json['app']
    if permissions and app != package_name and 'InterApp' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    # noinspection PyShadowingBuiltins
    dir: str = f'./Users/{username}/Library/Data/'
    data: dict = json.loads(request.json['data']) if isinstance(request.json['data'], str) else request.json['data']
    with open(f'{dir}/{app}', 'w') as f:
        json.dump(data, f)
    return Response(status=200)
