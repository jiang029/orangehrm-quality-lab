import re

import requests


def login(base_url, username, password):
    """完成 OrangeHRM Session 登录并返回登录过程中的响应。"""

    # 登录页和登录提交必须复用同一个 Session，确保 CSRF Token 与 Cookie 匹配。
    session = requests.Session()

    login_page_url = f"{base_url}/web/index.php/auth/login"
    login_page_response = session.get(login_page_url)

    # CSRF Token 来自登录页 HTML，提交账号密码时必须一并发送。
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
        # 登录成功和失败都可能返回 302，因此保留原始响应以检查 Location。
        allow_redirects=False,
    )

    return session, login_page_response, login_response
