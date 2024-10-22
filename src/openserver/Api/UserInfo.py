import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime, UTC
from flask import Response
from openserver.Helpers.Report import report, DirectoryEscalation


async def main(config, request) -> (dict, Response):
    username = request.json['username']
    if '/' in username:
        report(config, DirectoryEscalation)
        return Response(status=403)
    with open(f'./Users/{username}/.ID') as f:
        id: dict = json.load(f)
    id.update({'chamychain_public_key': '****************************************************************'})
    id.pop('chamychain_private_key')
    id.update({'rsa_public_key': serialization.load_pem_private_key(
        id['rsa_private_key'].encode(),
        password=None,
        backend=default_backend()
    ).public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()})
    id.pop('rsa_private_key')
    id.update({'plus': (id['settings']['plus_tier'] if int(datetime.now(UTC).strftime('%Y%m%d')) < id['settings']['plus_until'] else 0)})
    id.update({'profile_photo': f"http{'s' if config.Serve.Secure else ''}://{config.Serve.Domain}/protocols/profile-photos/{username}.png"})
    for key in id['settings']['profile_privacy']:
        id[key] = ['*' for _ in range((len(str(id[key]))))]
    id.pop('settings')
    id.pop('password')
    return id
