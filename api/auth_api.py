import re

import requests


def login(base_url, username, password):
    """完成 OrangeHRM Session 登录并返回登录过程中的响应。"""

    # Session 会跨请求保存 Cookie。登录页和登录提交必须复用同一个 Session，
    # 才能让 HTML 中的 CSRF Token 与服务端发放的匿名 Session Cookie 保持匹配。
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
        # 登录端点接收的是 HTML 表单数据，因此使用 data=，而不是 JSON 请求体。
        data={
            "_token": csrf_token,
            "username": username,
            "password": password,
        },
        # 登录成功和失败都可能返回 302；禁止自动跟随跳转后，测试才能通过
        # 原始 Location 区分跳往 Dashboard 的成功结果和返回 Login 的失败结果。
        allow_redirects=False,
    )

    return session, login_page_response, login_response
