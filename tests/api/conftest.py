import os
import time

import pytest

from api.auth_api import login
from api.employee_api import EmployeeAPI


BASE_URL = os.getenv(
    "ORANGEHRM_BASE_URL",
    "https://opensource-demo.orangehrmlive.com",
)


@pytest.fixture(scope="session")
def login_context():
    """登录一次并在本次测试会话结束后关闭 Session。"""

    # Pytest 应保持非交互运行，凭证从环境变量读取，避免写入源码或 Git。
    username = os.getenv("ORANGEHRM_USERNAME")
    password = os.getenv("ORANGEHRM_PASSWORD")
    if not username or not password:
        pytest.skip(
            "需要设置 ORANGEHRM_USERNAME 和 ORANGEHRM_PASSWORD",
        )

    session, login_page_response, login_response = login(
        BASE_URL,
        username,
        password,
    )

    yield {
        "session": session,
        "login_page_response": login_page_response,
        "login_response": login_response,
    }

    session.close()


@pytest.fixture(scope="session")
def employee_api(login_context):
    """验证登录前置条件，并提供共享认证状态的员工请求对象。"""

    login_page_response = login_context["login_page_response"]
    login_response = login_context["login_response"]
    login_location = login_response.headers.get("Location", "")

    assert login_page_response.status_code == 200
    assert login_response.status_code == 302
    assert login_location.endswith("/dashboard/index")

    return EmployeeAPI(login_context["session"], BASE_URL)


@pytest.fixture
def created_employee(employee_api):
    """为单条测试创建独立员工，并在测试结束后清理。"""

    # 公共 Demo 数据会变化，动态 Employee ID 可以降低与他人数据冲突的概率。
    employee_id = str(time.time_ns())[-10:]
    request_data = {
        "firstName": "Pytest",
        "middleName": "",
        "lastName": "Created",
        "employeeId": employee_id,
        "empPicture": None,
    }
    create_response = employee_api.create_employee(request_data)
    assert create_response.status_code == 200

    created_data = create_response.json()["data"]
    employee_context = {
        "request_data": request_data,
        "create_response": create_response,
        "created_data": created_data,
        "employee_id": employee_id,
        "emp_number": created_data["empNumber"],
        "deleted": False,
    }

    yield employee_context

    # yield 之后属于 teardown；即使测试断言失败，也会尽量删除临时员工。
    if not employee_context["deleted"]:
        cleanup_response = employee_api.delete_employee(
            employee_context["emp_number"],
        )
        # 404 表示员工已被测试步骤删除或被公共环境清理，同样没有数据残留。
        assert cleanup_response.status_code in (200, 404)
