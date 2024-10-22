import jwt


def get_login(config, request) -> tuple[str, list[str], str]:
    username = request.json.get('current_user_username', None)
    if username is None:
        coded = jwt.decode(request.json.get('cred'), config.Serve.Secret, algorithms=['HS256'])
        username = coded['username']
        permissions = coded['permissions']
        package_name = coded['package']
    else:
        permissions = None
        package_name = None
    return username, permissions, package_name
