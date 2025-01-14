import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime, UTC
import os
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> dict:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        id = {
            "birthday": "2000-01-01",
            "country": "US",
            "gender": "Male",
            "phone_number": "+10000000000",
            "postcode": "00000",
            "timezone": 0,
            "name": "Test",
            "surname": "USER",
            "settings": {
                "plus_until": 20000000,
                "plus_tier": 0,
                "theme_color": "blank",
                "profile_privacy": []
            },
            "rsa_private_key": "",
            "rsa_public_key": ""
        }
    else:
        with open(f'./Users/{username}/.ID') as f:
            id: dict = json.load(f)
    id.update({'chamychain_public_key': '****************************************************************'})
    if username != 'Guest':
        id.update({'rsa_public_key': serialization.load_pem_private_key(
            id['rsa_private_key'].encode(),
            password=None,
            backend=default_backend()
        ).public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()})
    id.update({'plus': (id['settings']['plus_tier'] if int(datetime.now(UTC).strftime('%Y%m%d')) < id['settings']['plus_until'] else 0)})
    id.update({'profile_photo': f"http{'s' if config.Serve.Secure else ''}://{config.Serve.Domain}/protocols/profile-photos/{username}.png"})
    if username == 'Guest':
        id['settings'].update({'apps': {}})
    else:
        id['settings'].update({'apps': os.listdir(f"./Users/{username}/Library/Data/")})
    if permissions and 'HiddenInformation' not in permissions:
        for key in id['settings']['profile_privacy']:
            if isinstance(id[key], int):
                id[key] = 0
            elif isinstance(id[key], str):
                id[key] = ''
            elif isinstance(id[key], list):
                id[key] = []
            elif isinstance(id[key], dict):
                id[key] = {}
            else:
                id[key] = ['*' for _ in range((len(str(id[key]))))]
        id.pop('settings')
    if permissions and 'RSA' not in permissions:
        id.pop('rsa_private_key')
        id.pop('rsa_public_key')
    return id
