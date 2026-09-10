from dataclasses import dataclass, field
import os
import re
from urllib.parse import urlparse

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@dataclass(frozen=True)
class UISettings:
    """保存 UI 环境配置，同时避免失败输出直接展示密码。"""

    base_url: str
    username: str
    password: str = field(repr=False)


@pytest.fixture(scope="session")
def ui_settings():
    """提供本地 UI 测试配置，并阻止用例误跑到公共 Demo。"""

    # session scope 只读取并校验一次不会变化的环境配置；浏览器页面仍由
    # pytest-playwright 按测试隔离，配置复用不会让不同用例共享页面状态。
    required_variables = (
        "ORANGEHRM_BASE_URL",
        "ORANGEHRM_USERNAME",
        "ORANGEHRM_PASSWORD",
    )
    missing_variables = [
        variable_name
        for variable_name in required_variables
        if not os.getenv(variable_name)
    ]
    if missing_variables:
        missing_text = ", ".join(missing_variables)
        pytest.skip(f"本地 UI 测试缺少环境变量: {missing_text}")

    base_url = os.environ["ORANGEHRM_BASE_URL"].rstrip("/")
    local_hosts = {"127.0.0.1", "localhost", "::1"}
    if urlparse(base_url).hostname not in local_hosts:
        pytest.skip("ui marker 只允许连接本机 OrangeHRM")

    return UISettings(
        base_url=base_url,
        username=os.environ["ORANGEHRM_USERNAME"],
        password=os.environ["ORANGEHRM_PASSWORD"],
    )


@pytest.fixture
def logged_in_page(page, ui_settings):
    """为员工 UI 用例提供独立且已经登录的浏览器页面。"""

    # fixture 默认是 function scope，并依赖插件提供的 function-scope page；
    # 每条测试都拥有隔离的 BrowserContext，不会共享 Cookie 或页面状态。
    login_page = LoginPage(page, ui_settings.base_url)
    login_page.open()
    login_page.login(ui_settings.username, ui_settings.password)
    expect(page).to_have_url(re.compile(r"/dashboard/index/?$"))
    expect(login_page.dashboard_heading).to_be_visible()

    # page 的关闭由 pytest-playwright 管理，这里只返回完成 Arrange 的页面，
    # 因而不需要再写一层重复 teardown。
    return page


@pytest.fixture
def ui_employee_data(employee_data, employee_api):
    """为 UI Create 生成数据，并在测试后通过现有 API 清理。"""

    # function scope 让每条 UI Create 测试拥有独立数据；依赖 employee_api
    # 只是为了 teardown，不会用 API 代替当前测试真正要验证的 UI 创建动作。
    yield employee_data

    # 即使 UI 断言失败，只要页面已成功创建员工，yield 后的清理仍会执行。
    search_response = employee_api.search_employee(employee_data["employeeId"])
    assert search_response.status_code == 200
    exact_matches = [
        employee
        for employee in search_response.json()["data"]
        if employee["employeeId"] == employee_data["employeeId"]
    ]
    for employee in exact_matches:
        cleanup_response = employee_api.delete_employee(employee["empNumber"])
        assert cleanup_response.status_code in (200, 404)
