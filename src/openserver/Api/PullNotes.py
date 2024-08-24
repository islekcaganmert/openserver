import os

import jwt


async def folder_to_dict(path):
    r = {}
    for v in os.listdir(path):
        if os.path.isfile(f'{path}{v}'):
            with open(f'{path}{v}', 'r') as f:
                r.update({v: f.read()})
        else:
            r.update({v: await folder_to_dict(f'{path}{v}/')})
    return r


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return {}
    return await folder_to_dict(f'./Users/{username}/Notes/')
