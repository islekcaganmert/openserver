import jwt
from flask import Response
from openserver.Helpers.Communications import DB


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return Response(status=200)
    DB(username).move_mail(request.json['mailbox'], request.json['mail'], request.json['move_to'])
    return Response(status=200)
