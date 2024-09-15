from flask import send_file


async def main(_, creds, method, path, data: bytes = None):
    path = f"./Users/{creds['username']}/Documents/{path}".replace('//', '/').removesuffix('/')
    if method == 'GET':
        return send_file(open(path, 'rb'), download_name=path.split('/')[-1])
    elif method == 'POST':
        with open(path, 'wb') as f:
            f.write(data)
        return str(len(data))
