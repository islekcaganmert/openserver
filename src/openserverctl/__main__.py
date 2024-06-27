import os
import sys
from openserverctl.setup import main as setup

raw_args = sys.argv
args = []
kwargs = {}
raw_args.pop(0)
while len(raw_args) > 0:
    if raw_args[0].startswith('--'):
        kwargs.update({raw_args[0].removeprefix('--'): raw_args[1]})
        raw_args.pop(1)
    if raw_args[0].startswith('-'):
        kwargs.update({raw_args[0].removeprefix('-'): True})
    else:
        args.append(raw_args[0])
    raw_args.pop(0)


if __name__ == '__main__':
    if not os.listdir('./'):
        setup()
    elif os.listdir('./') != ['Server.yaml', 'profile_picture.png', 'ToS.html', 'Feed', 'Users', 'Templates']:
        print('This is not a OpenServer generated directory. Please change directory to your data folder.')
    else:
        if len(args) == 0:
            print('Available commands: users, feed, search, web, rules')
        elif args[0] == 'users':
            # argument check
            pass  # continue with account ctl
        elif args[0] == 'feed':
            # argument check
            pass  # continue with feed ctl
        elif args[0] == 'search':
            # argument check
            pass  # continue with search ctl
        elif args[0] == 'web':
            # argument check
            pass  # continue with web ctl
        elif args[0] == 'rules':
            # argument check
            pass  # continue with rules ctl
