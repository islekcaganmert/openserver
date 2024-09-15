from datetime import datetime
import subprocess
import jwt
import os


async def main(config, request):
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    if username == 'Guest':
        return []
    if 'Documents' not in os.listdir(f"./Users/{username}/"):
        os.mkdir(f"./Users/{username}/Documents")
    r = {}
    for i in os.listdir(f"./Users/{username}/Documents"):
        r.update({i: {
            "type": subprocess.check_output(f"file -b './Users/{username}/Documents/{i}'", shell=True).decode().strip(),
            "size": os.path.getsize(f"./Users/{username}/Documents/{i}"),
            "created": datetime.fromtimestamp(os.path.getctime(f"./Users/{username}/Documents/{i}")).strftime('%Y-%m-%d %H:%M'),
            "edited": datetime.fromtimestamp(os.path.getmtime(f"./Users/{username}/Documents/{i}")).strftime('%Y-%m-%d %H:%M')
        }})
    return r
