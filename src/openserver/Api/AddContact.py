import json
from flask import Response
from openserver.Helpers.Report import report
import openserver.Helpers.Report as Report


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if '/' in request.json['email']:
        report(Report.DirectoryEscalation)
        return Response(status=403)
    path: str = f'./Users/{request.json['current_user_username']}/Contacts/{request.json['email']}.json'
    with open(path, 'w') as f:
        json.dump({
            "Relation": request.json['relation'],
            "SMTP": json.loads(request.json['smtp']),
            "Socials": json.loads(request.json['socials'])
        }, f)
    return Response(status=200)
