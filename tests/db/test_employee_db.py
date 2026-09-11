import json

import allure
import pytest

from utils.db import fetch_one


EMPLOYEE_BY_NUMBER_SQL = """
    SELECT
        emp_number,
        employee_id,
        emp_firstname,
        emp_middle_name,
        emp_lastname
    FROM hs_hr_employee
    WHERE emp_number = %s
"""


@allure.feature("PIM")
@allure.story("Employee Data Consistency")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.db
def test_create_employee_persists_to_database(
    employee_api,
    employee_data,
    db_connection,
):
    # Arrange｜Factory 已生成独立请求数据；emp_number 用于失败时也能通过 API 清理。
    emp_number = None

    try:
        with allure.step("通过 API 创建员工并确认接口结果"):
            # Act｜当前用例的业务动作必须在测试主体中可见。
            create_response = employee_api.create_employee(employee_data)
            create_body = create_response.json()
            created_data = create_body.get("data") or {}
            emp_number = created_data.get("empNumber")

            # Assert｜先严格确认 API 响应，再查询数据库最终状态。
            assert create_response.status_code == 200
            assert emp_number is not None
            assert created_data["employeeId"] == employee_data["employeeId"]
            assert created_data["firstName"] == employee_data["firstName"]
            assert created_data["middleName"] == employee_data["middleName"]
            assert created_data["lastName"] == employee_data["lastName"]

        with allure.step("查询数据库并核对员工最终状态"):
            employee_row = fetch_one(
                db_connection,
                EMPLOYEE_BY_NUMBER_SQL,
                (emp_number,),
            )
            allure.attach(
                json.dumps(employee_row, ensure_ascii=False, indent=2),
                name="Employee database row",
                attachment_type=allure.attachment_type.JSON,
            )

            assert employee_row is not None
            assert employee_row["emp_number"] == emp_number
            assert employee_row["employee_id"] == employee_data["employeeId"]
            assert employee_row["emp_firstname"] == employee_data["firstName"]
            assert employee_row["emp_middle_name"] == employee_data["middleName"]
            assert employee_row["emp_lastname"] == employee_data["lastName"]
    finally:
        # Cleanup｜数据库 SELECT 只负责断言，测试数据仍通过已有 API 删除。
        if emp_number is not None:
            cleanup_response = employee_api.delete_employee(emp_number)
            assert cleanup_response.status_code in (200, 404)


@pytest.mark.db
def test_update_employee_persists_to_database(
    employee_api,
    created_employee,
    db_connection,
):
    # Arrange｜既有 fixture 负责创建和 teardown，本用例只准备更新后的姓名。
    updated_last_name = "Updated"
    personal_details = {
        "firstName": created_employee["request_data"]["firstName"],
        "middleName": "",
        "lastName": updated_last_name,
        "employeeId": created_employee["employee_id"],
        "otherId": "",
        "drivingLicenseNo": "",
        "drivingLicenseExpiredDate": None,
        "gender": None,
        "maritalStatus": "",
        "birthday": None,
        "nationalityId": None,
    }

    # Act｜通过现有 API Client 修改同一名员工。
    update_response = employee_api.update_personal_details(
        created_employee["emp_number"],
        personal_details,
    )
    updated_data = update_response.json()["data"]

    # Assert｜API 与数据库必须同时呈现更新后的字段值。
    assert update_response.status_code == 200
    assert updated_data["employeeId"] == personal_details["employeeId"]
    assert updated_data["firstName"] == personal_details["firstName"]
    assert updated_data["middleName"] == personal_details["middleName"]
    assert updated_data["lastName"] == personal_details["lastName"]

    employee_row = fetch_one(
        db_connection,
        EMPLOYEE_BY_NUMBER_SQL,
        (created_employee["emp_number"],),
    )

    assert employee_row is not None
    assert employee_row["emp_number"] == created_employee["emp_number"]
    assert employee_row["employee_id"] == personal_details["employeeId"]
    assert employee_row["emp_firstname"] == personal_details["firstName"]
    assert employee_row["emp_middle_name"] == personal_details["middleName"]
    assert employee_row["emp_lastname"] == personal_details["lastName"]


@pytest.mark.db
def test_delete_employee_removes_database_record(
    employee_api,
    created_employee,
    db_connection,
):
    # Arrange｜empNumber 是 API 和数据库共同使用的精确记录标识。
    emp_number = created_employee["emp_number"]

    # Act｜删除动作只通过 API 执行，不使用 SQL 改写业务状态。
    delete_response = employee_api.delete_employee(emp_number)

    # Assert｜先确认 API 删除结果，再用 SELECT 断言记录已不存在。
    assert delete_response.status_code == 200
    deleted_ids = delete_response.json()["data"]
    assert len(deleted_ids) == 1
    assert type(deleted_ids[0]) in (int, str)
    assert deleted_ids[0] in (emp_number, str(emp_number))

    employee_row = fetch_one(
        db_connection,
        EMPLOYEE_BY_NUMBER_SQL,
        (emp_number,),
    )
    assert employee_row is None

    # 只有数据库也确认不存在后才跳过 fixture cleanup；若断言失败，teardown 仍会补清理。
    created_employee["deleted"] = True
