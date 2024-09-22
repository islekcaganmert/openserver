import json
import jwt
import os


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Pictures/")
    prefix = request.json['date'].replace('-', '')
    r = []
    dir = sorted(os.listdir(f"./Users/{username}/Pictures/"))
    first_index = -1
    last_index = -1
    previous = None
    next = None
    for i in range(len(dir)):
        if dir[i].startswith(prefix):
            r.append(dir[i])
            if first_index == -1:
                first_index = i
            last_index = i
        elif first_index != -1:
            break
    if len(dir) > first_index > 0:
        previous = dir[first_index - 1][0:8]
        previous = f"{previous[0:4]}-{previous[4:6]}-{previous[6:8]}"
    if len(dir) > last_index >= 0:
        next = dir[last_index + 1][0:8]
        next = f"{next[0:4]}-{next[4:6]}-{next[6:8]}"
    return {
        'list': r,
        'previous': previous,
        'next': next
    }