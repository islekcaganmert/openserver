import jwt
from openserver.Helpers.Communications import DB
from flask import request


# Hacking
PlusHacking = 'Hacking.Cracking.Plus'
MisconfiguredPayload = 'Hacking.Payload.Misconfigured'
ModificationToImmutable = 'Hacking.Payload.Immutable'
DirectoryEscalation = 'Hacking.Filesystem.Directory'
PermissionDenied = 'Permission.Denied'


def report(config, reason: str) -> None:
    username = request.json.get('current_user_username', None)
    if username is None:
        secret = ''
        with open(f'Server.yaml') as f:
            for line in f:
                if 'Secret' in line:
                    secret = line.split(': ')[1].strip()
                    break
        username = jwt.decode(request.json.get('cred'), secret, algorithms=['HS256'])['username']
    if reason == PlusHacking:
        subject, body = 'Hacker Alert', f'"{username}" tried to get free subscription. Detected and blocked.'
    elif reason == MisconfiguredPayload:
        subject, body = 'Misconfigured Payload Sent', f'"{request.remote_addr}" sent a misconfigured payload. Connection dropped.'
    elif reason == ModificationToImmutable:
        subject, body = 'Immutable Payload Modification', f'"{username}" tried to modify an immutable ID key. Changes rejected.'
    elif reason == DirectoryEscalation:
        subject, body = 'Directory Escalation', f'"{username}" tried to escalate directory. Connection dropped.'
    elif reason == PermissionDenied:
        coded = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])
        subject, body = 'Permission Denied', f'"{coded["package"]}" tried to access a forbidden resource of {username}. Connection dropped.'
    else:
        return
    DB('Administrator').add_mail(
        subject=subject,
        sender='SYSTEM',
        to=['Administrator@{}'],
        cc=[],
        hashtag=None,
        body=body,
        encrypted=True
    )
