import platform
import distro
import json
import os


async def main(config, software_info) -> dict:
    users = []
    for i in os.listdir('./Users/'):
        if i not in ['.DS_Store']:
            users.append(i)
    system = platform.system()
    if system == "Linux":
        os_data = {"family": "Linux", "name": distro.name(pretty=True), "version": ''}
    elif system == "Darwin":
        os_data = {"family": "Darwin", "name": "macOS", "version": platform.mac_ver()[0]}
    elif system == "Windows":
        os_data = {"family": "NT", "name": "Windows", "version": platform.win32_ver()[1]}
    else:
        os_data = {"family": system, "name": system, "version": "0"}
    os_data.update({"arch": platform.machine().replace('arm64', 'AArch64')})
    membership_plans = []
    for i in config.Membership.__dict__:
        if isinstance(getattr(config.Membership, i), str):
            membership_plans.append({
                "name": i,
                "storage": config.Membership.__dict__[i]
            })
    return {
        "help": config.Policies.Help,
        "os": os_data,
        "rules": json.loads(config.Rules.json()),
        "software": json.loads(software_info.json()),
        "users": users,
        "membership_plans": membership_plans,
        "version": "3.1"
    }
