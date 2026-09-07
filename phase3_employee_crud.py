import getpass
import time

import requests

from api.auth_api import login
from api.employee_api import EmployeeAPI


BASE_URL = "https://opensource-demo.orangehrmlive.com"
EMPLOYEES_URL = f"{BASE_URL}/web/index.php/api/v2/pim/employees"

username = input("Username: ")
password = getpass.getpass("Password: ")

session = None
employee_api = None
created_emp_number = None

try:
    print("\n1. Login")
    session, login_page_response, login_response = login(
        BASE_URL,
        username,
        password,
    )
    print("GET login page:", login_page_response.status_code)
    assert login_page_response.status_code == 200

    login_location = login_response.headers.get("Location", "")
    print("POST login:", login_response.status_code)
    print("Redirect:", login_location)
    assert login_response.status_code == 302
    assert login_location.endswith("/dashboard/index")

    employee_api = EmployeeAPI(session, BASE_URL)

    print("\n2. Create employee")
    employee_id = str(time.time_ns())[-10:]
    first_name = "PhaseThree"
    last_name = "Created"

    create_response = employee_api.create_employee(
        {
            "firstName": first_name,
            "middleName": "",
            "lastName": last_name,
            "employeeId": employee_id,
            "empPicture": None,
        },
    )
    print("POST employee:", create_response.status_code)
    assert create_response.status_code == 200

    created_employee = create_response.json()["data"]
    created_emp_number = created_employee["empNumber"]
    print("employeeId:", created_employee["employeeId"])
    print("empNumber:", created_emp_number)
    assert created_employee["employeeId"] == employee_id
    assert created_employee["firstName"] == first_name
    assert created_employee["lastName"] == last_name

    print("\n3. Search created employee")
    search_response = employee_api.search_employee(employee_id)
    print("GET employees:", search_response.status_code)
    if search_response.status_code != 200:
        print("Search response:", search_response.text)
    assert search_response.status_code == 200

    search_results = search_response.json()["data"]
    assert len(search_results) == 1
    assert search_results[0]["empNumber"] == created_emp_number
    assert search_results[0]["employeeId"] == employee_id
    assert search_results[0]["firstName"] == first_name
    assert search_results[0]["lastName"] == last_name

    print("\n4. Update employee")
    updated_last_name = "Updated"
    update_response = employee_api.update_personal_details(
        created_emp_number,
        {
            "firstName": first_name,
            "middleName": "",
            "lastName": updated_last_name,
            "employeeId": employee_id,
            "otherId": "",
            "drivingLicenseNo": "",
            "drivingLicenseExpiredDate": None,
            "gender": None,
            "maritalStatus": "",
            "birthday": None,
            "nationalityId": None,
        },
    )
    print("PUT personal details:", update_response.status_code)
    assert update_response.status_code == 200
    assert update_response.json()["data"]["lastName"] == updated_last_name

    print("\n5. Search updated employee")
    updated_search_response = employee_api.search_employee(employee_id)
    print("GET updated employee:", updated_search_response.status_code)
    assert updated_search_response.status_code == 200

    updated_results = updated_search_response.json()["data"]
    assert len(updated_results) == 1
    assert updated_results[0]["empNumber"] == created_emp_number
    assert updated_results[0]["lastName"] == updated_last_name

    print("\n6. Delete employee")
    delete_response = employee_api.delete_employee(created_emp_number)
    print("DELETE employee:", delete_response.status_code)
    print("Delete response:", delete_response.text)
    assert delete_response.status_code == 200
    assert str(created_emp_number) in delete_response.json()["data"]
    created_emp_number = None

    print("\n7. Confirm deletion")
    deleted_search_response = employee_api.search_employee(employee_id)
    print("GET deleted employee:", deleted_search_response.status_code)
    assert deleted_search_response.status_code == 200
    assert deleted_search_response.json()["data"] == []

    print("\n8. Verify unauthenticated request")
    unauthenticated_response = requests.get(
        EMPLOYEES_URL,
        params={"employeeId": employee_id},
    )
    print("GET without session:", unauthenticated_response.status_code)
    assert unauthenticated_response.status_code == 401

    unauthenticated_error = unauthenticated_response.json()["error"]
    assert unauthenticated_error["status"] == 401
    assert unauthenticated_error["message"] == "Session expired"

    print("\nPhase 3 employee CRUD flow passed.")
finally:
    if created_emp_number is not None and employee_api is not None:
        cleanup_response = employee_api.delete_employee(created_emp_number)
        print("\nCleanup employee:", cleanup_response.status_code)
