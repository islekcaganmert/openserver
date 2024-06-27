import json
import os


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return {}
    r = {}
    path: str = f'./Users/{request.json['current_user_username']}/Reminders/'
    for v in os.listdir(path):
        with open(f'{path}{v}', 'r') as f:
            r.update({v.removesuffix('.json'): json.load(f)})
    return r
