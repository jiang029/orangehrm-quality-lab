import getpass
import re

import requests

LOGIN_PAGE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/validate"

session = requests.Session()

login_page_response = session.get(LOGIN_PAGE_URL)
print("Login page status:", login_page_response.status_code)
print("Session cookie names:", session.cookies.keys())
assert login_page_response.status_code == 200

token_match = re.search(
    r':token="&quot;([^&]+)&quot;"',
    login_page_response.text,
)
print("CSRF token found:", token_match is not None)
assert token_match is not None
csrf_token = token_match.group(1)

username = input("Username: ")
password = getpass.getpass("Password: ")

login_response = session.post(
    LOGIN_URL,
    data={
        "_token": csrf_token,
        "username": username,
        "password": password,
    },
    allow_redirects=False,
)

location = login_response.headers.get("Location", "")
print("Login status:", login_response.status_code)
print("Redirect location:", location)

assert login_response.status_code == 302
assert location.endswith("/dashboard/index")
