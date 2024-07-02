import json
import os
import random
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from openserver.Helpers.Communications import DB
from flask import Response
from datetime import datetime, UTC
import hashlib
import openserver.Helpers.IdEntryValidation as validate


async def main(config, args):

    new_id = {}

    try:
        for i in [
            "birthday",
            "country",
            "gender",
            "phone_number",
            "postcode",
            "timezone"
        ]:
            if not getattr(validate, i)(args.json[i]):
                print(i)
                return Response(status=403)
            new_id.update({i: args.json[i]})

        # registering
        new_id.update({'name': ' '.join([i.capitalize() for i in args.json['name'].split(' ')])})
        new_id.update({'surname': args.json['surname'].upper()})
        new_id.update({'password': hashlib.sha3_512(args.json['password'].encode()).hexdigest()})
        new_id.update({'rsa_private_key': rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        ).private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()})
        new_id.update({'settings': {
            'plus_until': int(datetime.now(UTC).strftime('%Y%m%d')),
            'plus_tier': 0,
            'theme_color': 'blank',
            'profile_privacy': config.AccountDefaults.ProfilePrivacy
        }})
        for i in args.json['username']:
            if i not in 'abcdefghijklmnopqrstuvwxyz0123456789-':
                return Response(status=403)
        new_id.update({'chamychain_private_key': random.randint(
            1000000000000000000000000000000000000000000000000000000000000000,
            9999999999999999999999999999999999999999999999999999999999999999
        )})
        os.mkdir(f'./Users/{args.json['username']}/')
        with open(f'./Users/{args.json['username']}/.ID', 'w') as f:
            json.dump(new_id, f)
        for i in ['Library', 'Contacts', 'Library/Data', 'Notes', 'Reminders', 'Documents', 'Pictures', 'Movies', 'Music']:
            os.mkdir(f'./Users/{args.json['username']}/{i}/')
        os.system(f'cp -r ./profile_picture.png ./Users/{args.json['username']}/.PP.png')
        mails = DB(args.json['username'], create_now=True)
        with open(f'./Templates/SignUpEmail.html', 'r') as f:
            sign_up_email = f.read()
            sign_up_email_title = sign_up_email.split('<title>')[1].split('</title>')[0]
        mails.add_mail(
            sign_up_email_title,
            f'Administrator@{config.Serve.Domain}',
            [f"{args.json['username']}@{config.Serve.Domain}"],
            [],
            None,
            sign_up_email,
            encrypted=True
        )
        with open(f"./Users/{args.json['username']}/Contacts/{args.json['username']}@{config.Serve.Domain}.json", 'w') as f:
            json.dump({
                "Relation": "Self",
                "SMTP": {},
                "Socials": {}
            }, f)

    except KeyError:
        return Response(status=403)

    return Response(status=200)
