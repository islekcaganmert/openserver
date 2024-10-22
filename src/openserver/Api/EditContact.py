from flask import Response
from TheProtocols import Deleted
import json
import os
from openserver.Helpers.Report import report, DirectoryEscalation, PermissionDenied
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'ContactsWrite' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if '/' in request.json['email']:
        report(config, DirectoryEscalation)
        return Response(status=403)
    path: str = f"./Users/{username}/Contacts/{request.json['email']}.json"
    if request.json['data'] == Deleted():
        os.remove(path)
    else:
        with open(path, 'w') as f:
            json.dump(json.loads(request.json['data']) if isinstance(request.json['data'], str) else request.json['data'], f)
    return Response(status=200)
