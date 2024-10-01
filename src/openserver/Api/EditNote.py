from TheProtocols import Deleted
from flask import Response
import os
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied, DirectoryEscalation


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'NotesWrite' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    print(request.json['path'])
    path: list[str] = request.json['path'].split('/')
    if '..' in path:
        report(config, DirectoryEscalation)
        return Response(status=403)
    value: str = request.json['value']
    if path[0] == '':
        path.pop(0)
    directory: str = f'./Users/{username}/Notes'
    while len(path) != 1:
        if path[0] not in os.listdir(directory):
            os.mkdir(f'{directory}/{path[0]}')
        directory += f'/{path[0]}'
        if os.path.isfile(directory):
            os.remove(directory)
            os.mkdir(directory)
        path.pop(0)
    filename: str = path[0]
    print(f'{directory}/{filename}')
    if filename in os.listdir(directory):
        if os.path.isfile(f'{directory}/{filename}'):
            os.remove(f'{directory}/{filename}')
        else:
            os.system(f'rm -rf {directory}/{filename}')
    if value in [Deleted(), '<removed/>']:
        if os.path.isfile(f'{directory}/{filename}'):
            os.remove(f'{directory}/{filename}')
        else:
            os.rmdir(f'{directory}/{filename}')
    else:
        with open(f'{directory}/{filename}', 'w') as f:
            f.write(value)
    return Response(status=200)
