import re

import pytest
from playwright.sync_api import expect

from pages.employee_page import EmployeePage


@pytest.mark.ui
@pytest.mark.smoke
def test_create_employee_through_ui(logged_in_page, ui_employee_data):
    # Arrange｜Factory 只准备动态姓名和 Employee ID；员工尚未被 API 创建。
    employee_page = EmployeePage(logged_in_page)
    employee_page.open_employee_list()
    employee_page.open_add_employee()

    # Act｜输入和保存均依赖 Locator 的 actionability 自动等待，不使用固定 sleep。
    employee_page.create_employee(ui_employee_data)

    # Assert｜保存后进入新员工个人详情，并回显 UI 实际提交的核心字段。
    expect(logged_in_page).to_have_url(
        re.compile(r"/pim/viewPersonalDetails/empNumber/\d+$")
    )
    expect(employee_page.personal_details_heading).to_be_visible()
    expect(employee_page.first_name_input).to_have_value(
        ui_employee_data["firstName"]
    )
    expect(employee_page.last_name_input).to_have_value(
        ui_employee_data["lastName"]
    )
    expect(employee_page.employee_id_input).to_have_value(
        ui_employee_data["employeeId"]
    )


@pytest.mark.ui
@pytest.mark.smoke
def test_search_existing_employee_through_ui(
    logged_in_page,
    created_employee,
):
    # Arrange｜员工由成熟的 API fixture 创建并在 yield 后清理，UI 只验证查询链路。
    employee_page = EmployeePage(logged_in_page)
    employee_page.open_employee_list()

    # Act｜按本次运行动态生成的 Employee ID 查询。
    employee_page.search_by_employee_id(created_employee["employee_id"])

    # Assert｜web-first assertion 会重试到异步刷新的结果行出现。
    result_row = employee_page.result_row(created_employee["employee_id"])
    expect(result_row).to_have_count(1)
    expect(result_row).to_contain_text(
        created_employee["request_data"]["firstName"]
    )
    expect(result_row).to_contain_text(
        created_employee["request_data"]["lastName"]
    )


@pytest.mark.ui
def test_search_missing_employee_shows_no_records(
    logged_in_page,
    employee_data,
):
    # Arrange｜Factory 生成未创建的动态 Employee ID，避免写死可能被占用的值。
    employee_page = EmployeePage(logged_in_page)
    employee_page.open_employee_list()

    # Act
    employee_page.search_by_employee_id(employee_data["employeeId"])

    # Assert
    # 页面同时显示持久结果文字（span）和短暂 toast（p）；用元素语义区分两种
    # 同文案反馈，避免 first/nth 在 DOM 顺序变化时悄悄选错目标。
    expect(employee_page.no_records_message).to_be_visible()
    # 结果 table 此时只剩一个表头 row，没有任何员工数据 row。
    expect(employee_page.table.get_by_role("row")).to_have_count(1)
