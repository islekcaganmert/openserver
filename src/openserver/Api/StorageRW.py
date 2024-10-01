import jwt
from flask import send_file


async def main(config, creds, method, path, data: bytes = None):
    coded = jwt.decode(creds['token'], config.Serve.Secret, algorithms=['HS256'])
    if method == 'GET' and 'ReadFile' not in coded['permissions']:
        return '', 403
    if method == 'POST' and 'WriteFile' not in coded['permissions']:
        return '', 403
    path = f"./Users/{creds['username']}/Documents/{path}".replace('//', '/').removesuffix('/')
    if method == 'GET':
        return send_file(open(path, 'rb'), download_name=path.split('/')[-1])
    elif method == 'POST':
        with open(path, 'wb') as f:
            f.write(data)
        return str(len(data))
