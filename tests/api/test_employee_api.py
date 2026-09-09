import pytest

from tests.data.employee_data import build_employee_data, load_employee_cases


# 测试模块加载时，JSON 已通过标准库转换成 Python list/dict。
# ids 的列表推导式只提取每组 case 的可读名称，让 Pytest 报告仍容易定位失败场景。
EMPLOYEE_CASES = load_employee_cases()


@pytest.mark.smoke
@pytest.mark.regression
def test_create_employee(employee_api, employee_data):
    # Arrange｜准备测试前置和输入数据
    # employee_data 只生成独立请求数据，不会提前调用 Create 接口；
    # emp_number 用于记录创建结果，让 finally 在断言失败时仍能清理数据。
    emp_number = None
    created_data = {}

    try:
        # Act｜执行当前真正要验证的业务动作
        # Create 在测试主体内显式发生，因此读代码即可看出本用例验证的动作。
        create_response = employee_api.create_employee(employee_data)
        create_response_body = create_response.json()
        created_data = create_response_body.get("data") or {}
        emp_number = created_data.get("empNumber")

        # Assert｜验证 HTTP 结果和关键业务结果
        assert create_response.status_code == 200
        assert created_data["employeeId"] == employee_data["employeeId"]
        assert created_data["firstName"] == employee_data["firstName"]
        assert created_data["lastName"] == employee_data["lastName"]
    finally:
        # Cleanup｜Create 成功后必须删除临时员工；finally 保证业务断言失败时也会执行。
        if emp_number is not None:
            cleanup_response = employee_api.delete_employee(emp_number)
            assert cleanup_response.status_code in (200, 404)


# JSON 只保存两条已经真实确认的业务 case；动态姓名和 Employee ID 仍在运行时
# 由 Factory 生成。这让固定规则与易冲突的运行时数据各自放在合适的位置。
@pytest.mark.regression
@pytest.mark.parametrize(
    "employee_case",
    EMPLOYEE_CASES,
    ids=[case["case_id"] for case in EMPLOYEE_CASES],
)
def test_create_employee_rejects_empty_required_name(
    employee_api,
    employee_case,
):
    # Arrange｜准备测试前置和输入数据
    # ** 会把 {字段名: 输入值} 展开为关键字参数，交给 Factory 的 overrides。
    # 因而每组 case 都先生成完整合法 payload，再只覆盖当前需要验证的字段。
    invalid_employee_data = build_employee_data(
        **{employee_case["field"]: employee_case["value"]}
    )
    unexpected_emp_number = None

    try:
        # Act｜执行当前真正要验证的业务动作
        response = employee_api.create_employee(invalid_employee_data)
        response_body = response.json()
        unexpected_data = response_body.get("data") or {}
        unexpected_emp_number = unexpected_data.get("empNumber")

        # Assert｜验证 HTTP 结果和关键业务结果
        # expected 来自已经验证过的固定 JSON case，而不是在测试中重复写死。
        assert response.status_code == employee_case["expected_http_status"]
        error = response_body["error"]
        assert error["status"] == employee_case["expected_error_status"]
        assert error["message"] == employee_case["expected_message"]
        assert error["data"]["invalidParamKeys"] == [employee_case["field"]]
    finally:
        # 正常规则下不会创建员工；若 Demo 行为变化却意外成功，仍立即清理数据。
        if unexpected_emp_number is not None:
            cleanup_response = employee_api.delete_employee(unexpected_emp_number)
            assert cleanup_response.status_code in (200, 404)


@pytest.mark.smoke
@pytest.mark.regression
def test_search_created_employee(employee_api, created_employee):
    # Arrange｜准备测试前置和输入数据
    # created_employee fixture 已为本测试创建独立员工，并会在测试结束后清理。
    employee_id = created_employee["employee_id"]
    emp_number = created_employee["emp_number"]

    # Act｜执行当前真正要验证的业务动作
    # 使用刚创建的动态 Employee ID 查询，避免依赖公共 Demo 中不稳定的固定数据。
    response = employee_api.search_employee(employee_id)

    # Assert｜验证 HTTP 结果和关键业务结果
    # 除了成功状态码，还确认查询结果就是 Arrange 阶段创建的同一名员工。
    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert results[0]["empNumber"] == emp_number
    assert results[0]["employeeId"] == employee_id


@pytest.mark.regression
def test_update_employee_and_search_again(employee_api, created_employee):
    # Arrange｜准备测试前置和输入数据
    # created_employee 提供已经存在的员工；更新 payload 保留原有关键字段，
    # 只把 lastName 改为本测试关注的新值。
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

    # Act｜执行当前真正要验证的业务动作
    update_response = employee_api.update_personal_details(
        created_employee["emp_number"],
        personal_details,
    )

    # Assert｜验证 HTTP 结果和关键业务结果
    assert update_response.status_code == 200
    assert update_response.json()["data"]["lastName"] == updated_last_name

    # 再次查询属于状态验证：确认修改已持久化，而不只是相信 PUT 响应。
    search_response = employee_api.search_employee(
        created_employee["employee_id"],
    )
    assert search_response.status_code == 200
    results = search_response.json()["data"]
    assert len(results) == 1
    assert results[0]["lastName"] == updated_last_name


@pytest.mark.regression
def test_delete_employee_and_search_again(employee_api, created_employee):
    # Arrange｜准备测试前置和输入数据
    # fixture 创建的 empNumber 是后端记录主键，Delete 接口依靠它定位员工。
    emp_number = created_employee["emp_number"]

    # Act｜执行当前真正要验证的业务动作
    delete_response = employee_api.delete_employee(
        emp_number,
    )

    # Assert｜验证 HTTP 结果和关键业务结果
    assert delete_response.status_code == 200
    deleted_ids = delete_response.json()["data"]
    # 官方 Demo 曾返回字符串 ID，本地 5.9 返回整数 ID；先严格确认只删除一条，
    # 再只接受这两种已确认的表示，避免把其他 JSON 类型误判为同一个主键。
    assert len(deleted_ids) == 1
    assert type(deleted_ids[0]) in (int, str)
    assert deleted_ids[0] in (emp_number, str(emp_number))

    # Delete 后再次 Search，确认员工已无法查询，而不是只检查删除状态码。
    search_response = employee_api.search_employee(
        created_employee["employee_id"],
    )
    assert search_response.status_code == 200
    assert search_response.json()["data"] == []
    # 告知 fixture 数据已由本测试删除，teardown 无需再发送一次 Delete。
    created_employee["deleted"] = True
