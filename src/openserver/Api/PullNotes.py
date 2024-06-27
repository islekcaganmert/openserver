import os


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
    if request.json['current_user_username'] == 'Guest':
        return {}
    return await folder_to_dict(f'./Users/{request.json['current_user_username']}/Notes/')
