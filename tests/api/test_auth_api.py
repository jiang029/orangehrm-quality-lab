import os

import requests


BASE_URL = os.getenv(
    "ORANGEHRM_BASE_URL",
    "https://opensource-demo.orangehrmlive.com",
)
EMPLOYEES_URL = f"{BASE_URL}/web/index.php/api/v2/pim/employees"


def test_login_success(login_context):
    login_page_response = login_context["login_page_response"]
    login_response = login_context["login_response"]
    session = login_context["session"]
    login_location = login_response.headers.get("Location", "")

    assert login_page_response.status_code == 200
    assert len(session.cookies) > 0
    assert login_response.status_code == 302
    assert login_location.endswith("/dashboard/index")


def test_employee_search_requires_authentication():
    # 不使用登录 Session，验证服务端确实会拦截未认证的员工查询。
    response = requests.get(
        EMPLOYEES_URL,
        params={"employeeId": "0000000000"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["status"] == 401
    assert response.json()["error"]["message"] == "Session expired"
