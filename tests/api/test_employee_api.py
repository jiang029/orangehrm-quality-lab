def test_create_employee(created_employee):
    create_response = created_employee["create_response"]
    request_data = created_employee["request_data"]
    created_data = created_employee["created_data"]

    assert create_response.status_code == 200
    assert created_data["employeeId"] == request_data["employeeId"]
    assert created_data["firstName"] == request_data["firstName"]
    assert created_data["lastName"] == request_data["lastName"]


def test_search_created_employee(employee_api, created_employee):
    # Create 后再次 Search，验证数据不仅在创建响应中存在，也能被系统查询到。
    response = employee_api.search_employee(created_employee["employee_id"])

    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert results[0]["empNumber"] == created_employee["emp_number"]
    assert results[0]["employeeId"] == created_employee["employee_id"]


def test_update_employee_and_search_again(employee_api, created_employee):
    updated_last_name = "Updated"
    update_response = employee_api.update_personal_details(
        created_employee["emp_number"],
        {
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
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["data"]["lastName"] == updated_last_name

    # 再次查询用于确认修改已经持久化，而不只是 PUT 响应返回成功。
    search_response = employee_api.search_employee(
        created_employee["employee_id"],
    )
    assert search_response.status_code == 200
    results = search_response.json()["data"]
    assert len(results) == 1
    assert results[0]["lastName"] == updated_last_name


def test_delete_employee_and_search_again(employee_api, created_employee):
    delete_response = employee_api.delete_employee(
        created_employee["emp_number"],
    )

    assert delete_response.status_code == 200
    assert str(created_employee["emp_number"]) in delete_response.json()["data"]

    # Delete 后再次 Search，确认员工已无法查询，而不是只检查删除状态码。
    search_response = employee_api.search_employee(
        created_employee["employee_id"],
    )
    assert search_response.status_code == 200
    assert search_response.json()["data"] == []
    created_employee["deleted"] = True
