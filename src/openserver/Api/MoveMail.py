from flask import Response
from openserver.Helpers.Communications import DB
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'Mail' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    DB(username).move_mail(request.json['mailbox'], request.json['mail'], request.json['move_to'])
    return Response(status=200)
