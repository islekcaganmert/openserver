from openserver.Helpers.Report import report, PermissionDenied
from openserver.Helpers.Communications import DB
from openserver.Helpers.GetLogin import get_login
from flask import Response


async def main(config, request) -> (list, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return {}
    if permissions and 'Chat' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    return DB(username).list_chats()
