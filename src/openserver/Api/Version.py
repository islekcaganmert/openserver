import platform
import json
import os


async def main(config, software_info):
    users = []
    for i in os.listdir('./Users/'):
        if i not in ['.DS_Store']:
            users.append(i)
    system = platform.system()
    if system == "Linux":
        distro_info = platform.linux_distribution()
        os_data = {"family": "Linux", "name": distro_info[0], "version": distro_info[1]}
    elif system == "Darwin":
        os_data = {"family": "Darwin", "name": "macOS", "version": platform.mac_ver()[0]}
    elif system == "Windows":
        os_data = {"family": "NT", "name": "Windows", "version": platform.win32_ver()[1]}
    else:
        os_data = {"family": system, "name": system, "version": "0"}
    os_data.update({"arch": platform.machine().replace('arm64', 'AArch64')})
    return {
        "help": config.Policies.Help,
        "os": os_data,
        "rules": json.loads(config.Rules.json()),
        "software": json.loads(software_info.json()),
        "users": users,
        "version": "3.0"
    }
