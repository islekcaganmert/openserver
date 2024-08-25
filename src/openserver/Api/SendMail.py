import json

import asyncio

import jwt

from openserver.Helpers.Communications import DB
from flask import Response
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from TheProtocols import User
from openserver.Api.CurrentUserInfo import main as current_user_info


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    mail = {
        "body": request.json['body'],
        "cc": request.json['cc'].split(';'),
        "hashtag": None if request.json['hashtag'] == '' else request.json['hashtag'],
        "sender": f"{username}@{config.Serve.Domain}",
        "subject": request.json['subject'],
        "to": request.json['to'].split(';')
    }
    DB(username).add_mail(mailbox='Sent', encrypted=True, **mail)
    mail_temp = {i: mail[i] for i in mail}
    mail_temp.update({'add_to': ''})
    receivers = []
    for i in [
        mail['to'],
        mail['cc'],
        request.json['bcc'].split(';')
    ]:
        for j in i:
            if j != '' and j not in receivers:
                receivers.append(j)
    signature = serialization.load_pem_private_key(
        (await current_user_info(config, request)).get('rsa_private_key').encode(),
        password=None,
        backend=default_backend()
    ).sign(
        json.dumps(mail).encode(),
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
                DB(username).add_mail(encrypted=True, **mail)
            else:
                try:
                    conns.append(asyncio.create_task(requests.post(
                        f"https://{receiver.split('@')[1]}/protocols/lowend/add_mail_to_server",
                        json={
                            'add_to': receiver.split('@')[0],
                            'encrypted_object': serialization.load_pem_public_key(
                                User(receiver).rsa_public_key.encode(),
                                backend=default_backend()
                            ).encrypt(
                                json.dumps(mail).encode(),
                                padding.OAEP(
                                    mgf=padding.MGF1(algorithm=hashes.SHA512()),
                                    algorithm=hashes.SHA512(),
                                    label=None
                                )
                            ).hex(),
                            'signature': signature
                        }
                    )))
                except ValueError:
                    pass
    for conn in conns:
        await conn
    return Response(status=200)
