import json
from flask import Response
from openserver.Helpers.Report import report, PermissionDenied, DirectoryEscalation
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
    with open(path, 'w') as f:
        json.dump({
            "Relation": request.json['relation'],
            "Socials": request.json['socials']
        }, f)
    return Response(status=200)
