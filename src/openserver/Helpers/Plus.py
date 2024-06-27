from datetime import datetime, UTC


def check_plus(id: dict) -> int:
    if int(datetime.now(UTC).strftime('%Y%m%d')) < id['settings']['plus_until']:
        return id['settings']['plus_tier']
    else:
        return 0
