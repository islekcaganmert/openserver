from openserver.Helpers.Report import report, PermissionDenied
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from openserver.Api.CurrentUserInfo import main as current_user_info
from flask import Response
import requests
import json
import os
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (Response, dict):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and ('IoT' not in permissions or 'IoT-Full' not in permissions):
        report(config, PermissionDenied)
        return Response(status=403)
    if 'IoT.json' in os.listdir(f"./Users/{username}/Library/"):
        with open(f"./Users/{username}/Library/IoT.json") as f:
            d = json.load(f)
    else:
        d = {}
    url = d['things'][request.json['thing']]['url']
    if '://' not in url:
        url = f"https://{url}"
    url += '/protocols/lowend/get_thing'
    resp = requests.post(url, json={
        "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "user": f"{username}@{config.Serve.Secret}",
        "signature": serialization.load_pem_private_key(
            (await current_user_info(config, request)).get('rsa_private_key').encode(),
            password=None,
            backend=default_backend()
        ).sign(
            json.dumps({
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "user": f"{username}@{config.Serve.Secret}",
            }).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        ).hex()
    })
    if resp.status_code != 200:
        return Response(status=resp.status_code)
    return resp.json()
