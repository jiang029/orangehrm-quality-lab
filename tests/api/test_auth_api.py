import os

import pytest
import requests


BASE_URL = os.getenv(
    "ORANGEHRM_BASE_URL",
    "https://opensource-demo.orangehrmlive.com",
)
EMPLOYEES_URL = f"{BASE_URL}/web/index.php/api/v2/pim/employees"


@pytest.mark.smoke
@pytest.mark.regression
def test_login_success(login_context):
    # Arrange｜准备测试前置和输入数据
    # login_context 是 session-scope fixture，进入测试前已经完成一次真实登录；
    # 此处取得完整过程响应，是为了分别验证登录页、Cookie 和重定向结果。
    login_page_response = login_context["login_page_response"]
    login_response = login_context["login_response"]
    session = login_context["session"]

    # Act｜登录动作已由 fixture setup 完成，这里取得待验证结果
    # 读取原始 Location 是为了保留登录端点的直接结果，
    # 防止 Requests 自动跟随重定向后丢失登录端点返回的 302 信息。
    login_location = login_response.headers.get("Location", "")

    # Assert｜验证 HTTP 结果和关键业务结果
    assert login_page_response.status_code == 200
    assert len(session.cookies) > 0
    assert login_response.status_code == 302
    assert login_location.endswith("/dashboard/index")


@pytest.mark.regression
def test_employee_search_requires_authentication():
    # Arrange｜准备测试前置和输入数据
    # 故意不使用 login_context 或 EmployeeAPI，确保请求不携带认证 Session。
    search_params = {"employeeId": "0000000000"}

    # Act｜执行当前真正要验证的业务动作
    # params 会由 Requests 编码到 URL 查询字符串；查询条件只说明“查谁”，
    # 并不能替代 Cookie 所代表的身份认证。
    response = requests.get(
        EMPLOYEES_URL,
        params=search_params,
    )

    # Assert｜验证 HTTP 结果和关键业务结果
    assert response.status_code == 401
    assert response.json()["error"]["status"] == 401
    assert response.json()["error"]["message"] == "Session expired"
