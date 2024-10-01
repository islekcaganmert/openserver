from openserver.Helpers.Plus import check_plus
import json
import os
from openserver.Helpers.GetLogin import get_login
from openserver.Helpers.Report import report, PermissionDenied
from flask import Response


async def get_folder_size(path: str) -> int:
    size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            size += os.stat(fp).st_size
        for d in dirs:
            size += await get_folder_size(os.path.join(root, d))
    return size


async def main(config, request) -> (dict, Response):
    username, permissions, package_name = get_login(config, request)
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
    if permissions and 'ReadFile' not in permissions:
        report(config, PermissionDenied)
        return Response(status=403)
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
