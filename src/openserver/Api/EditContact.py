import jwt
from flask import Response
from TheProtocols import Deleted
import json
import os
from openserver.Helpers.Report import report
import openserver.Helpers.Report as Report


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if '/' in request.json['email']:
        report(Report.DirectoryEscalation)
        return Response(status=403)
    path: str = f'./Users/{username}/Contacts/{request.json['email']}.json'
    if request.json['data'] == Deleted():
        os.remove(path)
    else:
        with open(path, 'w') as f:
            json.dump(json.loads(request.json['data']) if isinstance(request.json['data'], str) else request.json['data'], f)
    return Response(status=200)
