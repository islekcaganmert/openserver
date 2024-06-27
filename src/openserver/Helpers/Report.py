from openserver.Helpers.Communications import DB
from flask import request


# Hacking
PlusHacking = 'Hacking.Cracking.Plus'
MisconfiguredPayload = 'Hacking.Payload.Misconfigured'
ModificationToImmutable = 'Hacking.Payload.Immutable'
DirectoryEscalation = 'Hacking.Filesystem.Directory'


def report(reason):
    if reason == PlusHacking:
        subject, body = 'Hacker Alert', f'"{request.json["current_user_username"]}" tried to get free subscription. Detected and blocked.'
    elif reason == MisconfiguredPayload:
        subject, body = 'Misconfigured Payload Sent', f'"{request.remote_addr}" sent a misconfigured payload. Connection dropped.'
    elif reason == ModificationToImmutable:
        subject, body = 'Immutable Payload Modification', f'"{request.json["current_user_username"]}" tried to modify an immutable ID key. Changes rejected.'
    elif reason == DirectoryEscalation:
        subject, body = 'Directory Escalation', f'"{request.json["current_user_username"]}" tried to escalate directory. Connection dropped.'
    DB('Administrator').add_mail(
        subject=subject,
        sender='SYSTEM',
        to='Administrator@{}',
        cc='',
        hashtag=None,
        body=body,
        encrypted=True
    )
