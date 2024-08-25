from openserver.Helpers.Plus import check_plus
import json
import jwt
import os


async def get_folder_size(path):
    size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            size += os.stat(fp).st_size
        for d in dirs:
            size += await get_folder_size(os.path.join(root, d))
    return size


async def main(config, request) -> dict:
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return {
            'total': 0,
            'used': {
                'id': 0,
                'library_data': 0,
                'mails': 0,
                'notes': 0,
                'reminders': 0,
                # 'contacts': 0,
                # 'profile_photo': 0,
                'documents': 0,
                'movies': 0,
                'music': 0,
                'photos': 0
            }
        }
    with open(f'./Users/{username}/.ID') as f:
        id: dict = json.load(f)
    total_size_sym: str = getattr(config.Membership, check_plus(config, id))
    total_size = 1024
    for i in ['KB', 'MB', 'GB', 'TB', 'PB']:
        if total_size_sym.endswith(i):
            total_size *= int(total_size_sym.removesuffix(i))
            break
        else:
            total_size *= 1024
    return {
        'total': total_size,
        'used': {
            'id': len(str(id)),
            'library_data': await get_folder_size(f'./Users/{username}/Library/Data/'),
            'mails': os.stat(f'./Users/{username}/Library/Mails.db').st_size,
            'notes': await get_folder_size(f'./Users/{username}/Notes/'),  # //
            'reminders': await get_folder_size(f'./Users/{username}/Reminders/'),
            # 'contacts': await get_folder_size(f'./Users/{username}/Contacts/'),
            # 'profile_photo': os.stat(f'./Users/{username}/.PP.png').st_size,
            'documents': 0,
            'movies': 0,
            'music': 0,
            'photos': 0
        }
    }
