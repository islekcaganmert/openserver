from flask import Response
from TheProtocols import Deleted
import json
import os
from openserver.Helpers.Report import report
import openserver.Helpers.Report as Report


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if '/' in request.json['email']:
        report(Report.DirectoryEscalation)
        return Response(status=403)
    path: str = f'./Users/{request.json['current_user_username']}/Contacts/{request.json['email']}.json'
    if request.json['data'] == Deleted():
        os.remove(path)
    else:
        with open(path, 'w') as f:
            json.dump(json.loads(request.json['data']), f)
    return Response(status=200)
