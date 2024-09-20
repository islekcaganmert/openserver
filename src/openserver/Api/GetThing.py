from openserver.Api.CurrentUserInfo import main as current_user_info
from flask import Response
import requests
import json
import jwt
import os


async def main(config, request) -> Response:
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
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
        return {}, resp.status_code
    return resp.json(), 200