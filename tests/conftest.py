import os

import pytest

from api.auth_api import login
from api.employee_api import EmployeeAPI
from tests.data.employee_data import build_employee_data


OFFICIAL_DEMO_BASE_URL = "https://opensource-demo.orangehrmlive.com"
# 以下账号密码由 OrangeHRM 官方公共 Demo 登录页明确公开，只用于该测试环境。
# 私有或其他环境仍必须通过环境变量提供凭证，不能复用这里的 Demo 默认值。
OFFICIAL_DEMO_USERNAME = "Admin"
OFFICIAL_DEMO_PASSWORD = "admin123"

BASE_URL = os.getenv(
    "ORANGEHRM_BASE_URL",
    OFFICIAL_DEMO_BASE_URL,
)


@pytest.fixture(scope="session")
def login_context():
    """登录一次并在本次测试会话结束后关闭 Session。"""

    # session scope 表示所有依赖此 fixture 的测试复用同一次登录，
    # 既减少对公共 Demo 的重复请求，也让后续接口共享同一份认证 Cookie。
    # 环境变量拥有最高优先级，便于在不同环境使用各自的账号密码。
    username = os.getenv("ORANGEHRM_USERNAME")
    password = os.getenv("ORANGEHRM_PASSWORD")

    # 官方登录页会公开展示专用 Demo 凭证。只有当前地址确实是官方公共 Demo 时，
    # 才为缺失的对应环境变量补默认值；切换到其他环境时绝不会套用这些凭证。
    if BASE_URL.rstrip("/") == OFFICIAL_DEMO_BASE_URL:
        username = username or OFFICIAL_DEMO_USERNAME
        password = password or OFFICIAL_DEMO_PASSWORD

    if not username or not password:
        pytest.skip(
            "非官方 Demo 环境需要设置 ORANGEHRM_USERNAME 和 "
            "ORANGEHRM_PASSWORD",
        )

    session, login_page_response, login_response = login(
        BASE_URL,
        username,
        password,
    )

    # yield 之前是本 fixture 的 setup；字典中的响应供登录测试验证，
    # Session 则继续提供给依赖它的 employee_api fixture。
    yield {
        "session": session,
        "login_page_response": login_page_response,
        "login_response": login_response,
    }

    # 所有依赖此 fixture 的测试结束后才执行 teardown，统一释放网络连接资源。
    session.close()


@pytest.fixture(scope="session")
def employee_api(login_context):
    """验证登录前置条件，并提供共享认证状态的员工请求对象。"""

    # fixture dependency 会先执行 login_context；这里取得的是同一个已登录 Session，
    # 因而 EmployeeAPI 发出的请求会自动携带认证 Cookie。
    login_page_response = login_context["login_page_response"]
    login_response = login_context["login_response"]
    login_location = login_response.headers.get("Location", "")

    # 在公共前置中确认认证成功，可避免把登录失败误判成员工接口自身失败。
    assert login_page_response.status_code == 200
    assert login_response.status_code == 302
    assert login_location.endswith("/dashboard/index")

    return EmployeeAPI(login_context["session"], BASE_URL)


@pytest.fixture
def employee_data():
    """为单条测试生成独立的 Create Employee 请求数据，但不发送请求。"""

    # fixture 默认是 function scope，因此每个测试会得到一份新的可变字典，
    # 不会因其他测试修改数据而相互污染。
    # 动态姓名和 Employee ID 的构造细节集中在 Factory，fixture 只负责在每个
    # 测试开始前调用一次，使测试继续拥有清晰且独立的数据生命周期。
    return build_employee_data()


@pytest.fixture
def created_employee(employee_api, employee_data):
    """为需要既有员工的单条测试准备数据，并在测试结束后清理。"""

    # 对 Search / Update / Delete 测试而言，员工已经存在只是 Arrange 前置，
    # 因此 Create 放在 fixture 中；Create 接口本身的测试会在测试函数内显式发请求。
    create_response = employee_api.create_employee(employee_data)
    assert create_response.status_code == 200

    created_data = create_response.json()["data"]
    employee_context = {
        "request_data": employee_data,
        "employee_id": employee_data["employeeId"],
        "emp_number": created_data["empNumber"],
        "deleted": False,
    }

    # yield 把准备好的员工交给测试；测试无论通过还是断言失败，
    # Pytest 都会在之后回到 yield 下方执行 teardown。
    yield employee_context

    # Delete 测试会自行删除员工并把 deleted 设为 True，避免 teardown 重复请求。
    if not employee_context["deleted"]:
        cleanup_response = employee_api.delete_employee(
            employee_context["emp_number"],
        )
        # 404 表示记录已被测试步骤或公共环境删除，同样达到了不残留数据的目标；
        # 此容错只用于 cleanup，不会放宽测试主体中的业务断言。
        assert cleanup_response.status_code in (200, 404)
