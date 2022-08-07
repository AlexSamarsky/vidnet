from datetime import datetime, timedelta


def set_cookie_with_token(response, name, token):
    params = {
        'expires': datetime.utcnow() + timedelta(days=15),
        'domain': None,
        'path': '/',
        'secure': True,
        'httponly': True
    }

    response.set_cookie(name, token, **params)
