import requests.exceptions
from jinja2 import Template
from TheProtocols import App
import jwt
from openserver.Helpers.Communications import DB
from datetime import datetime, UTC


async def main(config, request):
    app = App(request.json.get('package'), not config.Serve.Debug)
    with open(f'./Templates/SignInWarning.html') as f:
        t = f.read()
    try:
        DB(request.json.get('username')).add_mail(
            encrypted=True,
            body=Template(t).render(
                app=app,
                config=config,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '*'),
                time=datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
            ),
            cc=[],
            hashtag=None,
            sender='SYSTEM',
            subject=t.split('<title>')[1].split('</title>')[0],
            to=[f"{request.json.get('username')}@{config.Serve.Domain}"]
        )
    except requests.exceptions.ProxyError:
        DB(request.json.get('username')).add_mail(
            encrypted=True,
            body=Template(t).render(
                app=type('App', (), {
                    "name": "Unregistered App",
                    "icon": "",
                    "description": "",
                    "latest_version": "0.0.0",
                    "latest_build_number": 0,
                    "developer": "",
                    "preferences": {}
                }),
                config=config,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '*'),
                time=datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
            ),
            cc=[],
            hashtag=None,
            sender='SYSTEM',
            subject=t.split('<title>')[1].split('</title>')[0],
            to=[f"{request.json.get('username')}@{config.Serve.Domain}"]
        )
    return {"token": jwt.encode({
        "username": request.json.get('username'),
        "password": request.json.get('password'),
        "package": app.package_name,
        "permissions": request.json.get('permissions'),
        "ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', '*')
    }, config.Serve.Secret, algorithm='HS256')}
