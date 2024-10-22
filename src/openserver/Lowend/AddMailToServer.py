from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from openserver.Helpers.Communications import DB
from TheProtocols import User
from flask import Response
import json


async def main(_, request) -> Response:
    add_to: str = request.json.get('add_to', None)
    encrypted_object: str = request.json.get('encrypted_object', None)
    signature: str = request.json.get('signature', None)
    with open(f'./Users/{add_to}/.ID') as f:
        obj = json.loads(serialization.load_pem_private_key(
            json.load(f)['rsa_private_key'],
            password=None,
            backend=default_backend()
        ).decrypt(
            bytes.fromhex(encrypted_object),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None
            )
        ))
    try:
        serialization.load_pem_public_key(
            User(obj['sender']).rsa_public_key.encode(),
            backend=default_backend()
        ).verify(
            bytes.fromhex(signature),
            json.dumps(obj).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
    except InvalidSignature:
        return Response(status=403)
    DB(add_to).add_mail(encrypted=True, **obj)
    return Response(status=200)
