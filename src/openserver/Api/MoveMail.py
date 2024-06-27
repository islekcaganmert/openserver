from flask import Response
from Helpers.Communications import DB


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return Response(status=200)
    DB(request.json['current_user_username']).move_mail(request.json['mailbox'], request.json['mail'], request.json['move_to'])
    return Response(status=200)
