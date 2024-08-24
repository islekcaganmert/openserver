import json
from flask import Response
from TheProtocols import App, User
import jwt


async def main(config, request):
    app = App(request.json.get('package'), not config.Serve.Debug)
    dev = User(app.developer)
    permissions = request.json.get('permissions')
    permissions.sort()
    if dev.verify(request.json.get('signature'), json.dumps({
        "package": app.package_name,
        "permissions": permissions
    })):
        return {"token": jwt.encode({
            "username": request.json.get('username'),
            "password": request.json.get('password'),
            "package": app.package_name,
            "signature": request.json.get('signature'),
            "permissions": permissions,
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', '*')
        }, config.Serve.Secret, algorithm='HS256')}
    else:
        print('Invalid signature')
        return Response(status=401)
