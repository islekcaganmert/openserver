from TheProtocols import Struct
from flask import Flask, request, Response, send_file
import importlib.util
import hashlib
import yaml
import json
import sys
import os
import asyncio

version = '1.0.0'


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


server = Flask('OpenServer')
with open(sys.argv[1], 'r') as f:
    config = yaml.safe_load(f)
check_config()
config = Struct(config)
software_info = Struct({
    "build": 1,
    "channel": "Alpha",
    "developer": "islekcaganmert@hereus.net",
    "name": "OpenServer",
    "source": "https://github.com/islekcaganmert/openserver.git",
    "version": "1.0.0"
})


def check_password():
    if request.json['current_user_username'] == 'Guest':
        return True
    elif '/' in request.json['current_user_username']:
        return False
    elif request.json['current_user_username'] not in os.listdir('./Users/'):
        return False
    else:
        with open(f"./Users/{request.json['current_user_username']}/.ID", 'r') as f:
            id = json.load(f)
        return id['password'] == hashlib.sha3_512(request.json['current_user_password'].encode()).hexdigest()


@server.route('/protocols/lowend/<endpoint>', methods=['GET', 'POST'])
async def lowend_router(endpoint):
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
            'search': [request]

        }[endpoint]))
    except Exception as e:
        if config.Serve.Debug:
            raise e
        return Response(status=500)


@server.route('/protocols/profile-photos/<username>.png')
async def profile_photos(username):
    with open(f'./Users/{username}/.ID', 'r') as f:
        id = json.load(f)
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
    if '/' in request.json['current_user_username']:
        return Response(status=401)
    elif request.json['current_user_username'] not in os.listdir('./Users/'):
        return Response(status=401)
    else:
        with open(f"./Users/{request.json['current_user_username']}/.ID", 'r') as f:
            id = json.load(f)
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
    if '/' in request.json['current_user_username']:
        return Response(status=401)
    elif request.json['current_user_username'] not in os.listdir('./Users/'):
        return Response(status=401)
    else:
        with open(f"./Users/{request.json['current_user_username']}/.ID", 'r') as f:
            id = json.load(f)
        if id['password'] != hashlib.sha3_512(request.json['current_user_password'].encode()).hexdigest():
            return Response(status=401)
    os.system(f'rm -rf ./Users/{request.json["current_user_username"]}')
    return 'Account deleted'


if __name__ == '__main__':
    server.run(
        host=config.Serve.Host,
        port=config.Serve.Port,
        debug=config.Serve.Debug
    )
