import hashlib
import json
from flask import Response
import openserver.Helpers.IdEntryValidation as validate
from openserver.Helpers.Report import report, PermissionDenied, PlusHacking, ModificationToImmutable, MisconfiguredPayload
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'ModifyID' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    with open(f'./Users/{username}/.ID') as f:
        id: dict = json.load(f)

    key: str = request.json['key']
    value: (list, str, int) = request.json['data'] if request.json['data'] else ''

    if '/' in key:
        if key.split('/')[0] == 'settings' and len(key.split('/')) == 2:
            if key.split('/')[1] not in id['settings']:
                return Response(status=500)
            elif key.split('/')[1] in ['plus_until', 'plus_tier']:
                report(config, PlusHacking)
                return Response(status=403)
        else:
            return Response(status=500)
    elif key not in id:
        return Response(status=500)

    if key in config.Security.ImmutableIdEntries:
        report(config, ModificationToImmutable)
        return Response(status=403)

    if getattr(validate, key.replace('/', '_'))(value):
        if '/' in key:
            id['settings'].update({key.split('/')[1]: value})
        elif key == 'password':
            id.update({key: hashlib.sha3_512(request.json['password'].encode()).hexdigest()})
        else:
            id.update({key: value})
    else:
        report(config, MisconfiguredPayload)
        return Response(status=403)

    with open(f'./Users/{username}/.ID', 'w') as f:
        json.dump(id, f)
    return Response(status=200)
