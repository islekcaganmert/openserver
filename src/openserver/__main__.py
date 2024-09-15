import subprocess

import jwt

from openserver.Helpers.AppInfo import AppInfo
from TheProtocols.objects.network import Software
from flask import Flask, request, Response, send_file
import importlib.util
import hashlib
import yaml
import json
import sys
import os
# noinspection PyUnresolvedReferences
import asyncio


def check_config():
    if not ('Serve' in config and isinstance(config['Serve'], dict)):
        print('Config is misconfigured')
        sys.exit(1)
    if not ('Host' in config['Serve'] and isinstance(config['Serve']['Host'], str)):
        print('Host is not set')
        sys.exit(1)
    if not ('Port' in config['Serve'] and 1 < config['Serve']['Port'] < 9999):
        print('Port is invalid or not set')
        sys.exit(1)
    if not ('Debug' in config['Serve'] and isinstance(config['Serve']['Debug'], bool)):
        config['debug'] = False
    if not ('EnableStatic' in config['Serve'] and isinstance(config['Serve']['EnableStatic'], bool)):
        config['EnableStatic'] = False
    if not ('Rules' in config and [i for i in config['Rules']] == [
        'new_accounts_allowed'
    ] and (
                    isinstance(config['Rules']['new_accounts_allowed'], bool) and
                    True
            )):
        print('Rules are not set correctly')
        sys.exit(1)


class Config:
    def __init__(self, data: dict) -> None:
        self.Serve.Host = data['Serve']['Host']
        self.Serve.Port = data['Serve']['Port']
        self.Serve.Debug = data['Serve']['Debug']
        self.Serve.Secure = data['Serve']['Secure']
        self.Serve.Domain = data['Serve']['Domain']
        self.Serve.Secret = data['Serve']['Secret']
        self.Policies.ToS = data['Policies']['ToS']
        self.Policies.Help = data['Policies']['Help']
        self.Policies.Administrator = data['Policies']['Administrator']
        self.Rules = self.RulesO(**data['Rules'])
        self.Membership = self.MembershipO(data['Membership'])
        self.Security.ImmutableIdEntries = data['Security']['ImmutableIdEntries']
        self.AccountDefaults.ProfilePrivacy = data['AccountDefaults']['ProfilePrivacy']

    class Serve:
        Domain: str
        Port: int
        Host: str
        Debug: bool
        Secret: str

    class Policies:
        pass

    class RulesO:
        def __init__(self, new_accounts_allowed: bool) -> None:
            self.new_accounts_allowed: bool = new_accounts_allowed

        def json(self):
            # noinspection PyUnresolvedReferences
            return json.dumps({
                "new_accounts_allowed": self.new_accounts_allowed
            })

    class MembershipO:
        def __init__(self, data: dict) -> None:
            self.__dict__ = data
            self.order = [i for i in data]

        def __getattr__(self, item):
            return self.__dict__[item]

    class Security:
        ImmutableIdEntries = ["birthday", "gender", "name", "surname", "rsa_private_key"]

    class AccountDefaults:
        ProfilePrivacy = []


server = Flask('OpenServer')
with open('Server.yaml') as f:
    config = yaml.safe_load(f)
check_config()
config = Config(config)
software_info = Software(**{
    "build": int(subprocess.run("git rev-list --count --all".split(" "), capture_output=True).stdout.decode().strip()),
    # must be hardcoded before release
    "channel": "Stable",
    "developer": "islekcaganmert@hereus.net",
    "name": "OpenServer",
    "source": "https://github.com/islekcaganmert/openserver.git",
    "version":
        subprocess.run(["pip", "show", "openserver"], capture_output=True).stdout.decode().strip().split('\n')[1].split(
            ': ')[1]
})

if __name__ == '__main__':
    if not config.Serve.Debug:
        os.system(f"gunicorn -b {config.Serve.Host}:{config.Serve.Port} openserver.__main__:server")


def get_creds():
    if request.path == '/protocols/login':
        return {
            "username": request.json.get('username'),
            "password": request.json.get('password'),
        }
    elif request.json.get('cred', None) is None:
        return {
            "username": request.json.get('current_user_username'),
            "password": request.json.get('current_user_password'),
        }
    else:
        return jwt.decode(request.json['cred'], config.Serve.Secret, algorithms=['HS256'])


def check_password(token: str = None):
    if token is not None:
        cred = jwt.decode(token, config.Serve.Secret, algorithms=['HS256'])
    else:
        cred = get_creds()
    if cred['username'] == 'Guest':
        return True
    elif '/' in cred['username']:
        return False
    elif cred['username'] not in os.listdir('./Users/'):
        return False
    with open(f"./Users/{cred['username']}/.ID") as id_file:
        id = json.load(id_file)
    return id['password'] == hashlib.sha3_512(cred['password'].encode()).hexdigest()


@server.route('/protocols/lowend/<endpoint>', methods=['GET', 'POST'])
async def lowend_router(endpoint):
    # noinspection DuplicatedCode
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(current_dir, f"Lowend/{''.join([i.capitalize() for i in endpoint.split('_')])}.py")
    spec = importlib.util.spec_from_file_location(endpoint, relative_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        return await mod.main(config, *({

            'add_mail_to_server': [request],
            'add_message_to_server': [request]

        }[endpoint]))
    except Exception as e:
        if config.Serve.Debug:
            raise e
        return Response(status=500)


@server.route('/protocols/<endpoint>', methods=['GET', 'POST'])
async def server_router(endpoint):
    # noinspection DuplicatedCode
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(current_dir, f"Api/{''.join([i.capitalize() for i in endpoint.split('_')])}.py")
    spec = importlib.util.spec_from_file_location(endpoint, relative_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if endpoint not in ['version', 'terms_of_service', 'signup', 'user_info']:
        if not check_password():
            return Response(status=401)
    try:
        return await mod.main(config, *({

            'version': [software_info],
            'terms_of_service': [],
            'signup': [request],
            'current_user_info': [request],
            'set_user_data': [request],
            'get_feed': [],
            'get_feed_post': [request],
            'pull_library_data': [request],
            'push_library_data': [request],
            'pull_app_preferences': [request],
            'push_app_preferences': [request],
            'storage_status': [request],
            'pull_notes': [request],
            'edit_note': [request],
            'user_info': [request],
            'list_contacts': [request],
            'add_contact': [request],
            'create_reminder': [request],
            'create_reminder_list': [request],
            'get_reminders': [request],
            'create_sub_reminder': [request],
            'delete_reminder': [request],
            'list_mailboxes': [request],
            'get_mail': [request],
            'send_mail': [request],
            'move_mail': [request],
            'edit_contact': [request],
            'edit_reminder': [request],
            'list_chats': [request],
            'toggle_reminder': [request],
            'get_message': [request],
            'send_message': [request],
            'search': [request],
            'login': [request],
            'storage_ls': [request],
            'storage_new_folder': [request],
            'storage_delete': [request],

        }[endpoint]))
    except Exception as e:
        if config.Serve.Debug:
            raise e
        return Response(status=500)


@server.route('/protocols/storage/<username>/<path:path>', methods=['GET', 'POST'])
async def storage(username: str, path: str):
    # noinspection DuplicatedCode
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(current_dir, f"Api/StorageRW.py")
    spec = importlib.util.spec_from_file_location('storage_r_w', relative_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    creds = {'username': 'Guest', 'token': None}
    if request.headers.get('Authorization', None) is None:
        return Response(status=401)
    elif request.headers['Authorization'].split(' ')[0] == 'TheProtocols-Token':
        creds = {'username': username, 'token': request.headers['Authorization'].split(' ')[1]}
    else:
        return Response(status=401)
    if not check_password(token=creds['token']):
        return Response(status=401)
    path = ('/' + path + '/').replace('//', '/').replace('/../', '/')
    path = path.replace('/./', '/').removesuffix('/').removeprefix('/')
    return await mod.main(config, creds, request.method, path, **({'data': request.data} if request.method == 'POST' else {}))


@server.route('/protocols/profile-photos/<username>.png')
async def profile_photos(username):
    with open(f'./Users/{username}/.ID') as id_file:
        id = json.load(id_file)
    if 'profile_photo' in id['settings']['profile_privacy']:
        return send_file('./profile_photo.png')
    else:
        return send_file(f'./Users/{username}/.PP.png')


@server.route('/openserver/export-account', methods=['GET', 'POST'])
async def export_account():
    if request.method == 'GET':
        return '''
<form method="POST">
<input name="current_user_username" type="text" placeholder="Username">
<input name="current_user_password" type="password" placeholder="Password">
<input type="submit" value="Export">
</form>
        '''
    # noinspection DuplicatedCode
    if '/' in request.json['current_user_username']:
        return Response(status=401)
    elif request.json['current_user_username'] not in os.listdir('./Users/'):
        return Response(status=401)
    else:
        with open(f"./Users/{request.json['current_user_username']}/.ID") as id_file:
            id = json.load(id_file)
        if id['password'] != hashlib.sha3_512(request.json['current_user_password'].encode()).hexdigest():
            return Response(status=401)
    os.system(f'cd ./Users/{request.json["current_user_username"]}/; tar -czvf ../../export.tar.gz ./*')
    return send_file(f'./export.tar.gz')


@server.route('/openserver/delete-account', methods=['GET', 'POST'])
async def delete_account():
    if request.method == 'GET':
        return '''
<form method="POST">
<input name="current_user_username" type="text" placeholder="Username">
<input name="current_user_password" type="password" placeholder="Password">
<input type="submit" value="Delete">
</form>
        '''
    # noinspection DuplicatedCode
    if '/' in request.json['current_user_username']:
        return Response(status=401)
    elif request.json['current_user_username'] not in os.listdir('./Users/'):
        return Response(status=401)
    else:
        with open(f"./Users/{request.json['current_user_username']}/.ID") as id_file:
            id = json.load(id_file)
        if id['password'] != hashlib.sha3_512(request.json['current_user_password'].encode()).hexdigest():
            return Response(status=401)
    os.system(f'rm -rf ./Users/{request.json["current_user_username"]}')
    return 'Account deleted'


server.route('/.well-known/app_info.json', methods=['GET', 'POST'])(AppInfo(software_info, config))

if __name__ == '__main__':
    if config.Serve.Debug:
        server.run(
            host=config.Serve.Host,
            port=config.Serve.Port,
            debug=True
        )
