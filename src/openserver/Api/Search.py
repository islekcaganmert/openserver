import json
import os
from datetime import datetime
import asyncio

import jwt
from TheProtocols import User
from openserver.Helpers.Communications import DB
from openserver.Api.PullNotes import main as pull_notes
from openserver.Api.GetReminders import main as get_reminders


async def search_user(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    for username in os.listdir('./Users/'):
        try:
            if username.lower() in keys or f"{username}@{config.Serve.Domain}" in keys:
                user = json.load(open(f'./Users/{username}/.ID'))
                r.append({
                    'title': f"{user['name']} {user['surname']}",
                    'url': username if '@' in username else f"{username}@{config.Serve.Domain}",
                    'description': ''
                })
            for contact in os.listdir(f'./Users/{username}/Contacts/'):
                if contact.removesuffix('.json') in keys or contact.split('@')[0] in keys:
                    user = User(contact.removesuffix('.json'))
                    r.append({
                        'title': f"{user.name} {user.surname}",
                        'url': contact.removesuffix('.json'),
                        'description': ''
                    })
        except NotADirectoryError:
            pass
    return r


async def search_communications(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    username = request.json.get('current_user_username', None)
    if username is None:
        username = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])['username']
    comms = DB(username)
    mailboxes = comms.list_mailboxes()
    for mailbox in mailboxes:
        for i in range(1, mailboxes[mailbox] + 1):
            try:
                mail = comms.get_mail(mailbox, i)
                count = 0
                for word in [
                    str(mail['hashtag']),
                    mail['date_received'].split(' ')[0],
                    mail['date_received'].split('-')[0],
                    mailbox,
                    'mail',
                    'mails',
                    datetime.strptime(mail['date_received'], '%Y-%m-%d %H:%M').strftime('%B'),
                ] + mail['body'].split(' ') + mail['subject'].split(' '):
                    if word.lower() in keys:
                        count += 1
                if count > 0:
                    r.append({
                        'title': mail['subject'],
                        'url': f"mail:{mailbox}/{i}",
                        'description': mail['body']
                    })
            except Exception as e:
                raise e
    chats = comms.list_chats()
    for chat in chats:
        if chats[chat]['participants'] in keys:
            r.append({
                'title': chats[chat]['title'],
                'url': chat,
                'description': ', '.join(chats[chat]['participants'])
            })
    return r


def search_notes_in(path, folder, keys):
    r = {}
    for i in folder:
        if isinstance(folder[i], dict):
            rl = search_notes_in(f'{path}{i}/', folder[i], keys)
            for key in rl:
                if key not in [i for i in r]:
                    r.update({key: []})
                r[key] += rl[key]
        else:
            count = 0
            for key in keys:
                pk = path.lower().split('/')
                pk.remove('')
                for word in i.lower().split(' ') + folder[i].lower().split(' ') + pk:
                    if word == key:
                        count += 1
            if count > 0:
                if count not in [i for i in r]:
                    r.update({str(count): []})
                r[str(count)].append({
                    'title': i,
                    'url': f"note:{path}{i}",
                    'description': ''
                })
    return r


async def search_notes(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    notes = await pull_notes(config, request)
    rl = search_notes_in('/', notes, keys)
    if rl != {}:
        for i in range(sorted([int(i) for i in rl])[-1] + 1):
            if i in [int(a) for a in rl]:
                for result in rl[str(i)]:
                    r.append(result)
    r.reverse()
    return r


async def search_reminders(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    reminders = await get_reminders(config, request)
    for listname in reminders:
        for word in listname.lower().split(' '):
            if word in keys:
                r.append({
                    'title': listname,
                    'url': f"reminder:{listname}",
                    'description': ''
                })
            for reminder in reminders[listname]:
                for i in [
                    reminder['deadline'],
                    reminder['deadline'].split(' ')[0],
                    reminder['deadline'].split('-')[0],
                ] + [a['title'] for a in reminder['subs']] + reminder['title'].lower().split(' '):
                    if i == word:
                        r.append({
                            'title': reminder['title'],
                            'url': f"reminder:{listname}/{reminder['title']}",
                            'description': ''
                        })
    return r


async def search_iot(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_files(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_music(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_tv(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_social(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_calendar(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_feed(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def search_web(config, request) -> list:
    keys = request.json['key'].lower().split(' ')
    r = []
    return r


async def main(config, request) -> dict:
    tasks = []
    # Advertise health part
    for i in [
        search_user,
        search_communications,
        search_notes,
        search_reminders,
        search_iot,
        search_files,
        search_music,
        search_tv,
        search_social,
        search_calendar,
        search_feed,
        search_web,
    ]:
        tasks += [i(config, request)]
    results = await asyncio.gather(*tasks)
    r = []
    for result in results:
        r += result
        if '://' not in r[-1]['url']:
            r[-1]['url'] = f"theprotocols://{r[-1]['url']}"
    return {'results': r}
