class EmployeeAPI:
    def __init__(self, session, base_url):
        self.session = session
        self.employees_url = f"{base_url}/web/index.php/api/v2/pim/employees"

    def create_employee(self, employee_data):
        return self.session.post(
            self.employees_url,
            json=employee_data,
        )

    def search_employee(self, employee_id):
        return self.session.get(
            self.employees_url,
            params={"employeeId": employee_id},
        )

    def update_personal_details(self, emp_number, personal_details):
        personal_details_url = (
            f"{self.employees_url}/{emp_number}/personal-details"
        )
        return self.session.put(
            personal_details_url,
            json=personal_details,
        )

    def delete_employee(self, emp_number):
        return self.session.delete(
            self.employees_url,
            json={"ids": [emp_number]},
        )
