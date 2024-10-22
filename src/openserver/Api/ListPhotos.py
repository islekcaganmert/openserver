from flask import Response
from openserver.Helpers.Report import report, PermissionDenied
import os
from openserver.Helpers.GetLogin import get_login


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
    if username == 'Guest':
        return Response(status=200)
    if permissions and 'PhotosRead' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
    if 'Pictures' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Pictures/")
    prefix = request.json['date'].replace('-', '')
    r = []
    ls = sorted(os.listdir(f"./Users/{username}/Pictures/"))
    first_index = -1
    last_index = -1
    previous = None
    nxt = None
    for i in range(len(ls)):
        if ls[i].startswith(prefix):
            r.append(ls[i])
            if first_index == -1:
                first_index = i
            last_index = i
        elif first_index != -1:
            break
    if len(ls) > first_index > 0:
        previous = ls[first_index - 1][0:8]
        previous = f"{previous[0:4]}-{previous[4:6]}-{previous[6:8]}"
    if len(ls) > last_index >= 0:
        nxt = ls[last_index + 1][0:8]
        nxt = f"{nxt[0:4]}-{nxt[4:6]}-{nxt[6:8]}"
    return {
        'list': r,
        'previous': previous,
        'next': nxt
    }
