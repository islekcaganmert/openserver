import json
import os
from flask import Response
from openserver.Helpers.Report import report, PermissionDenied
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return {}
    if permissions and 'Contacts' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    r = {}
    path: str = f'./Users/{username}/Contacts/'
    for v in os.listdir(path):
        with open(f'{path}{v}') as f:
            r.update({v.removesuffix('.json'): json.load(f)})
    return r
