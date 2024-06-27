from Helpers.Communications import DB


async def main(config, request):
    if request.json['current_user_username'] == 'Guest':
        return {}
    return DB(request.json['current_user_username']).get_mail(request.json['mailbox'], request.json['id'])
