import asyncio
import json
from openserver.Helpers.Communications import DB
from flask import Response
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from TheProtocols import User
from openserver.Api.CurrentUserInfo import main as current_user_info
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied


async def main(config, request) -> Response:
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'Chat' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if request.json['chat'] == '/':
        obj = json.loads(request.json['body']) if isinstance(request.json['body'], str) else request.json['body']
        if 'handler' not in obj:
            obj['handler'] = obj['id']
        if isinstance(obj['participants'], str):
            obj['participants'] = obj['participants'].split(';')
        if f"{username}@{config.Serve.Domain}" not in obj['participants']:
            obj['participants'].append(f"{username}@{config.Serve.Domain}")
        DB(username, create_now=True).add_chat(**obj)
        return Response(status=200)
    message = {
        "from": f"{username}@{config.Serve.Domain}",
        "body": request.json['body'],
        "chat": request.json['chat'],
    }
    current_db = DB(username)
    current_db.add_message(encrypted=True, body=message['body'], chat=message['chat'], sender=message['from'])
    message_temp = {i: message[i] for i in message}
    message_temp.update({'add_to': ''})
    receivers = current_db.get_chat(request.json['chat'])['participants']
    signature = serialization.load_pem_private_key(
        (await current_user_info(config, request))['rsa_private_key'].encode(),
        password=None,
        backend=default_backend()
    ).sign(
        json.dumps(message).encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA512()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA512()
    ).hex()
    conns = []
    for receiver in receivers:
        if receiver != '':
            if receiver.split('@')[1] == config.Serve.Domain:
                DB(username).add_message(encrypted=True, **message)
            else:
                conns.append(asyncio.create_task(requests.post(
                    f"https://{receiver.split('@')[1]}/protocols/lowend/add_message_to_server",
                    json={
                        'add_to': receiver.split('@')[0],
                        'encrypted_object': serialization.load_pem_public_key(
                            User(receiver).rsa_public_key.encode(),
                            backend=default_backend()
                        ).encrypt(
                            json.dumps(message).encode(),
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                                algorithm=hashes.SHA512(),
                                label=None
                            )
                        ).hex(),
                        'signature': signature
                    }
                )))
    for conn in conns:
        await conn
    return Response(status=200)
