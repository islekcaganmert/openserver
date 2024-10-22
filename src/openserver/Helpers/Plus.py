from datetime import datetime, UTC


def check_plus(config, id: dict) -> str:
    if int(datetime.now(UTC).strftime('%Y%m%d')) < id['settings']['plus_until']:
        return config.Membership.order[id['settings']['plus_tier']]
    else:
        return config.Membership.order[0]
