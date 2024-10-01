from openserver.Helpers.Report import report, PermissionDenied
from flask import Response
from openserver.Helpers.Communications import DB
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return {}
    if permissions and 'Chat' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    return DB(username).get_message(request.json['chat'], request.json['id'])
