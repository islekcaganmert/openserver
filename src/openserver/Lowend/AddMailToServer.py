from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from Helpers.Communications import DB
from TheProtocols import User
from flask import Response
import json


async def main(config, request):
    add_to: str = None
    encrypted_object: str = None
    signature: str = None
    for i in ['add_to', 'encrypted_object', 'signature']:
        if i in request.json:
            setattr(locals(), i, request.json[i])
        else:
            return Response(status=403)
    with open(f'./Users/{add_to}/.ID', 'r') as f:
        object = json.loads(serialization.load_pem_private_key(
            json.load(f)['rsa_private_key'],
            password=None,
            backend=default_backend()
        ).decrypt(
            encrypted_object,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None
            )
        ))
    try:
        serialization.load_pem_public_key(
            User(object['sender']).rsa_public_key.encode(),
            backend=default_backend()
        ).verify(
            signature,
            json.dumps(object).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
    except InvalidSignature:
        return Response(status=403)
    DB(add_to).add_mail(mailbox='Primary', encrypted=True, **object)
    return Response(status=200)
