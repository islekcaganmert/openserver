import json
from Helpers.Communications import DB
from flask import Response
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from TheProtocols import User
from Api.CurrentUserInfo import main as current_user_info


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    if request.json['chat'] == '/':
        obj = json.loads(request.json['body'])
        if 'handler' not in obj:
            obj['handler'] = obj['id']
        if isinstance(obj['participants'], str):
            obj['participants'] = obj['participants'].split(';')
        if f"{request.json['current_user_username']}@{config.Serve.Domain}" not in obj['participants']:
            obj['participants'].append(f"{request.json['current_user_username']}@{config.Serve.Domain}")
        DB(request.json['current_user_username'], create_now=True).add_chat(**obj)
        return Response(status=200)
    message = {
        "from": f"{request.json['current_user_username']}@{config.Serve.Domain}",
        "body": request.json['body'],
        "chat": request.json['chat'],
    }
    current_db = DB(request.json['current_user_username'])
    current_db.add_message(encrypted=True, **message)
    message_temp = {i: message[i] for i in message}
    message_temp.update({'add_to': ''})
    receivers = current_db.get_chat(request.json['chat'])['participants']
    signature = serialization.load_pem_private_key(
        current_user_info(config, request)['rsa_private_key'],
        password=None,
        backend=default_backend()
    ).sign(
        json.dumps(message).encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA512()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA512()
    )
    for receiver in receivers:
        if receiver != '':
            if receiver.split('@')[1] == config.Serve.Domain:
                DB(request.json['current_user_username']).add_message(encrypted=True, **message)
            else:
                requests.post(
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
                        ),
                        'signature': signature
                    }
                )
    return Response(status=200)
