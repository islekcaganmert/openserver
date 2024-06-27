import json
import os
import sys
import requests
import openserver.Helpers.IdEntryValidation as validate
from getpass import getpass
from datetime import datetime, UTC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import random
from openserver.Helpers.Communications import DB
from openserver.Api import Version as openserver_version
import hashlib

data = {
    "admin": {
        "country": "",
        "timezone": 0,
        "postcode": "",
        "name": "",
        "surname": "",
        "gender": "",
        "birthday": "",
        "phone_number": "",
        "password": "",
        'settings': {
            'plus_until': int(datetime.now(UTC).strftime('%Y%m%d')),
            'plus_tier': 0,
            'theme_color': 'blank',
            'profile_privacy': []
        },
        'rsa_private_key': rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        ).private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode(),
        'chamychain_private_key': random.randint(
            1000000000000000000000000000000000000000000000000000000000000000,
            9999999999999999999999999999999999999999999999999999999999999999
        )
    },
    "activation": "",
    "config": {
        "secure": True,
        "domain": "localhost",
        "support": "Support",
        "rules": {
            "new_accounts_allowed": True
        },
        "storage": ['100MB', '1GB', '5GB', '20GB']
    },
    "terms": ""
}


def yes_no(t):
    answer = ''
    while answer not in ['y', 'n']:
        answer = input(f'{t} (y/n) ')
    return answer == 'y'


class OOBE:
    @staticmethod
    def activation():
        print("\n\n\nActivate OpenServer\n")
        print("OpenServer is completely free and open source.")
        print("However if you want access to support and want guarantee, you must activate it with a license key.")
        print("If you don't activate, you will use upstream version. You can still get help from community.")
        print("Please do not activate if you want to use upstream, beta, or alpha versions.")
        print("Leave blank to skip activation")
        key = input("\nKey: ")
        data['activation'] = key

    @staticmethod
    def licenses():
        print('\n\n\nLicenses')
        print('''\n
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
        \n''')  # GPL
        if data['activation'] != '':
            print('Please read Terms of Service on https://github.com/islekcaganmert/openserver/blob/main/ToS.md\n')
        if not yes_no('Do you agree above?'):
            sys.exit(1)

    @staticmethod
    def admin():
        print("\n\n\nRegion\n")
        for i in [
            ['country', "Enter your country's two-letter code: ", str],
            ['timezone', "Enter your timezone: (ex. UTC-8) UTC", int],
            ['postcode', "Enter your postcode: ", str]
        ]:
            data['admin'][i[0]] = i[2](input(i[1]))
            while not getattr(validate, i[0])(data['admin'][i[0]]):
                print('Invalid input.')
                data['admin'][i[0]] = i[2](input(i[1]))
        data['admin']['country'] = data['admin']['country'].upper()
        print('\n\n\nAdministrator')
        if data['activation'] == '':
            data['admin']['name'] = ' '.join([i.capitalize() for i in input('Name: ').split(' ')])
            data['admin']['surname'] = input('Surname: ').upper()
            for i in [
                ['gender', "Gender: ", str],
                ['birthday', 'Birthday: ', str],
                ['phone_number', 'Phone Number: ', str]
            ]:
                data['admin'][i[0]] = i[2](input(i[1]))
                while not getattr(validate, i[0])(data['admin'][i[0]]):
                    print('Invalid input.')
                    data['admin'][i[0]] = input(i[1])
        else:
            activation_key_owner = requests.post(
                'https://islekcaganmert.vercel.app/Backend/OpenServer/Activation.py',
                json={'key': data['activation']}
            ).json()
            for i in ['name', 'surname', 'gender', 'birthday', 'phone_number']:
                print(i.replace('_', ' ').capitalize() + ': ' + activation_key_owner[i])
                data['admin'][i] = activation_key_owner[i]
        password, re_password = '1', '2'
        while password != re_password:
            password = getpass()
            re_password = getpass('Again: ')
        data['admin']['password'] = hashlib.sha3_512(password.encode()).hexdigest()

    @staticmethod
    def config():
        print('\n\n\nConfigure Network\n')
        data['config']['secure'] = input('Do you want to enable HTTPS? (Y/n) ') != 'n'
        if data['activation'] == '':
            data['config']['domain'] = input('Enter a domain: ')
        else:
            data['config']['domain'] = requests.post(
                'https://islekcaganmert.vercel.app/Backend/OpenServer/Activation.py',
                json={'key': data['activation']}
            ).json()['domain']
            print(f"Enter a domain: {data['config']['domain']}")
        data['config']['support'] = input('Enter support username: ')
        if input('Do you want to configure rules now? (Y/n) ') != 'n':
            data['config']['rules']['new_accounts_allowed'] = yes_no('Do you want to allow new accounts?')
        for i in range(4):
            inp = input(f'Enter storage limit for tier {i}: (ex. 100MB, 25GB, 2TB) ')
            ok = False
            for j in ['MB', 'GB', 'TB']:
                if inp.endswith(j):
                    try:
                        int(inp.removesuffix(j))
                        ok = True
                    except ValueError:
                        pass
            if ok:
                data['config']['storage'][i] = inp
        print('\nSetup wizard suggest you to check Server.yaml after setup for more configurations.')

    @staticmethod
    def terms():
        print('\n\n\nTerms of Service\n')
        with open('.OpenServer-Setup-Wizard', 'w') as f:
            f.write('<h1>Terms of Service</h1>\n')
        print('You will be redirected to your preferred text editor to write terms of service.')
        os.system(f"{input('Please enter the executable path of a text editor: ')} .OpenServer-Setup-Wizard")
        with open('.OpenServer-Setup-Wizard', 'r') as f:
            data['terms'] = f.read()
        os.remove('.OpenServer-Setup-Wizard')


class Install:
    @staticmethod
    def rootfs():
        for i in ['Feed', 'Templates', 'Users']:
            os.mkdir(i)
        for i in ['SignUpEmail']:
            with open(f'Templates/{i}.html', 'wb') as f:
                with requests.get(f'https://github.com/islekcaganmert/openserver/raw/master/Assets/Templates/{i}.html') as r:
                    f.write(r.content)
        with open(f'profile_picture.png', 'wb') as f:
            with requests.get(f'https://github.com/islekcaganmert/openserver/raw/master/Assets/profile_picture.png') as r:
                f.write(r.content)
        with open('ToS.html', 'w') as f:
            f.write(data['terms'])

    @staticmethod
    def config():
        with open('Server.yaml', 'a') as f:
            # Serve
            f.write('Serve:\n')
            f.write('    Host: "0.0.0.0"\n')
            f.write('    Port: 80\n')
            f.write('    Debug: false\n')
            f.write(f'    Secure: {"true" if data["config"]["secure"] else "false"}\n')
            f.write(f'    Domain: "{data["config"]["domain"]}"\n\n')
            # Policies
            f.write(f'Policies:\n')
            f.write('    ToS: "ToS.html"\n')
            f.write(f'    Help: "{data["config"]["support"]}"\n')
            f.write('    Administrator: "Administrator"\n\n')
            # Rules
            f.write('Rules:\n')
            for i in data['config']['rules']:
                f.write(f'    {i}: {"true" if data["config"]["rules"][i] else "false"}\n')
            # Storage
            f.write('\nStorage:\n')
            for i in range(4):
                f.write(f'    Plus{i}: {data["config"]["storage"][i]}\n')
            # Security
            f.write('\nSecurity:\n')
            f.write('    ImmutableIdEntries: ["birthday", "gender", "name", "surname", "rsa_private_key"]\n\n')
            # AccountDefaults
            f.write('AccountDefaults:\n')
            f.write('    ProfilePrivacy: []\n')

    @staticmethod
    def admin():
        os.mkdir(f'./Users/Administrator/')
        with open(f'./Users/Administrator/.ID', 'w') as f:
            json.dump(data['admin'], f)
        for i in ['Library', 'Contacts', 'Library/Data', 'Notes', 'Reminders', 'Documents', 'Pictures', 'Movies', 'Music']:
            os.mkdir(f'./Users/Administrator/{i}/')
        os.system(f'cp -r ./profile_picture.png ./Users/Administrator/.PP.png')
        mails = DB('Administrator', create_now=True)
        with open(f'./Templates/SignUpEmail.html', 'r') as f:
            sign_up_email = f.read()
            sign_up_email_title = sign_up_email.split('<title>')[1].split('</title>')[0]
        mails.add_mail(
            sign_up_email_title,
            f'Administrator@{data["config"]["domain"]}',
            [f"Administrator@{data["config"]["domain"]}"],
            [],
            None,
            sign_up_email
        )
        with open(f"./Users/Administrator/Contacts/Administrator@{data["config"]["domain"]}.json", 'w') as f:
            json.dump({
                "Relation": "Self",
                "SMTP": {},
                "Socials": {}
            }, f)

    @staticmethod
    def check_update():
        latest = requests.get('https://islekcaganmert.vercel.app/Backend/OpenServer/Update.py').content.decode()
        installed = openserver_version
        return latest == installed

    @staticmethod
    def update():
        latest = requests.get('https://islekcaganmert.vercel.app/Backend/OpenServer/Update.py').content.decode()
        filename = f"OpenServer-{latest}-py3-none-any.whl"
        os.system(f"wget https://github.com/islekcaganmert/openserver/releases/download/{latest}/{filename}")
        os.system(f"pip install ./{filename}")


def main():
    print("\nWelcome to OpenServer!")
    print("Setup Wizard will guide to setup your new network.")
    OOBE.activation()
    OOBE.licenses()
    OOBE.admin()
    OOBE.config()
    OOBE.terms()
    print('\n\n\nInstalling system\n')
    print('Getting Ready...', end=' ', flush=True)
    Install.rootfs()
    print('DONE!\nSetting up Server...', end=' ', flush=True)
    Install.config()
    print('DONE!\nSetting up Administrator...', end=' ', flush=True)
    Install.admin()
    print('DONE!\nChecking for updates...', end=' ', flush=True)
    ua = Install.check_update()
    if ua:
        print('FOUND!')
        Install.update()
    else:
        print('DONE!')
    print('\n\n\nSetup is completed.')
