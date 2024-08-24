import json
import os
import jwt


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return {}
    r = {}
    path: str = f'./Users/{username}/Reminders/'
    for v in os.listdir(path):
        with open(f'{path}{v}') as f:
            r.update({v.removesuffix('.json'): json.load(f)})
    return r
