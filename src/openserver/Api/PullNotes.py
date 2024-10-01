import os
from openserver.Helpers.GetLogin import get_login
from flask import Response
from openserver.Helpers.Report import report, PermissionDenied


async def folder_to_dict(path: str) -> dict:
    r = {}
    for v in os.listdir(path):
        if os.path.isfile(f'{path}{v}'):
            with open(f'{path}{v}') as f:
                r.update({v: f.read()})
        else:
            r.update({v: await folder_to_dict(f'{path}{v}/')})
    return r


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return {}
    if permissions and 'Notes' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    return await folder_to_dict(f'./Users/{username}/Notes/')
