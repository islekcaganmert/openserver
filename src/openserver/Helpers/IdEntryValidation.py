from datetime import datetime, UTC


def birthday(value: str) -> bool:
    try:
        if not (datetime.now(UTC).year - 150 <= int(value.split('-')[0]) <= datetime.now(UTC).year):
            return False
        elif int(value.split('-')[0]) == datetime.now(UTC).year:
            if int(value.split('-')[1]) > datetime.now(UTC).month:
                return False
        return True
    except ValueError:
        return False


def country(value: str) -> bool:
    return len(value) == 2 and isinstance(value, str) and value.upper() == value


def gender(value: str) -> bool:
    return value in [
        'Male', 'Female', 'Lesbian', 'Gay', 'Bisexual', 'Transgender', 'Queer', 'Intersexual', 'Asexual', 'Pansexual'
    ]


def phone_number(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not value.startswith('+'):
        return False
    try:
        int(value.removeprefix('+'))
    except ValueError:
        return False
    if len(value) not in range(12, 14):
        return False
    return True


def postcode(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    if len(value) != 5:
        return False
    return True


def timezone(value: int) -> bool:
    return isinstance(value, int) and -12 <= value <= 14


def settings_theme_color(value: str) -> bool:
    return value in ['red', 'orange', 'yellow', 'green', 'blue', 'pink', 'purple', 'blank', '']
