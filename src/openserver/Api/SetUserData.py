import hashlib
import json
from flask import Response
import openserver.Helpers.IdEntryValidation as validate
import openserver.Helpers.Report

Report = Helpers.Report
report = Report.report


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    username = request.json['current_user_username']
    with open(f'./Users/{username}/.ID', 'r') as f:
        id: dict = json.load(f)

    key: str = request.json['key']
    value: (list, str, int) = request.json['data'] if request.json['data'] else ''

    if '/' in key:
        if key.split('/')[0] == 'settings' and len(key.split('/')) == 2:
            if key.split('/')[1] not in id['settings']:
                return Response(status=500)
            elif key.split('/')[1] in ['plus_until', 'plus_tier']:
                report(Report.PlusHacking)
                return Response(status=403)
        else:
            return Response(status=500)
    elif key not in id:
        return Response(status=500)

    if key in config.Security.ImmutableIdEntries:
        report(Report.ModificationToImmutable)
        return Response(status=403)

    if getattr(validate, key.replace('/', '_'))(value):
        if '/' in key:
            id['settings'].update({key.split('/')[1]: value})
        elif key == 'password':
            id.update({key: hashlib.sha3_512(request.json['password'].encode()).hexdigest()})
        else:
            id.update({key: value})
    else:
        report(Report.MisconfiguredPayload)
        return Response(status=403)

    with open(f'./Users/{username}/.ID', 'w') as f:
        json.dump(id, f)
    return Response(status=200)
