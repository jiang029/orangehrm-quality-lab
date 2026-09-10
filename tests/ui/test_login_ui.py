import re

import allure
import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@allure.feature("Authentication")
@allure.story("Administrator Login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
@pytest.mark.smoke
def test_login_success(page, ui_settings):
    with allure.step("打开管理员登录页"):
        # Arrange｜直接打开本地登录页，并用语义化 Locator 找到可交互控件。
        login_page = LoginPage(page, ui_settings.base_url)
        login_page.open()

    with allure.step("管理员提交有效凭证"):
        # Act｜fill 和 click 会自动等待元素达到可操作状态，不需要固定 sleep。
        login_page.login(ui_settings.username, ui_settings.password)

    with allure.step("确认进入 Dashboard"):
        # Assert｜同时验证落地 URL 和用户可见的 Dashboard 标题。
        expect(page).to_have_url(re.compile(r"/dashboard/index/?$"))
        expect(login_page.dashboard_heading).to_be_visible()


@pytest.mark.ui
def test_login_rejects_invalid_password(page, ui_settings):
    # Arrange｜仍使用本地管理员用户名，但提供确定错误的密码。
    login_page = LoginPage(page, ui_settings.base_url)
    login_page.open()

    # Act｜Playwright 在输入、点击及页面反馈之间自动等待可操作状态。
    login_page.login(
        ui_settings.username,
        "definitely-not-the-local-password",
    )

    # Assert｜错误反馈对用户可见，且页面没有进入 Dashboard。
    expect(login_page.invalid_credentials_message).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login/?$"))
