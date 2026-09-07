import re

import requests


def login(base_url, username, password):
    session = requests.Session()

    login_page_url = f"{base_url}/web/index.php/auth/login"
    login_page_response = session.get(login_page_url)

    token_match = re.search(
        r':token="&quot;([^&]+)&quot;"',
        login_page_response.text,
    )
    assert token_match is not None
    csrf_token = token_match.group(1)

    login_url = f"{base_url}/web/index.php/auth/validate"
    login_response = session.post(
        login_url,
        data={
            "_token": csrf_token,
            "username": username,
            "password": password,
        },
        allow_redirects=False,
    )

    return session, login_page_response, login_response
