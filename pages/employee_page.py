import re

from playwright.sync_api import expect


class EmployeePage:
    """封装员工列表与新增员工链路中已经确认的重复页面行为。"""

    def __init__(self, page):
        self.page = page
        self.employee_information_heading = page.get_by_role(
            "heading",
            name="Employee Information",
        )
        self.add_employee_heading = page.get_by_role(
            "heading",
            name="Add Employee",
        )
        self.personal_details_heading = page.get_by_role(
            "heading",
            name="Personal Details",
        )
        self.first_name_input = page.get_by_placeholder("First Name")
        self.last_name_input = page.get_by_placeholder("Last Name")
        self.employee_id_input = (
            page.locator(".oxd-input-group")
            .filter(has_text="Employee Id")
            .get_by_role("textbox")
        )
        self.table = page.get_by_role("table")
        self.no_records_message = page.locator("span").filter(
            has_text=re.compile(r"^No Records Found$")
        )

    def open_employee_list(self):
        self.page.get_by_role("link", name="PIM", exact=True).click()
        # 这里是页面对象自身的就绪条件，不是业务断言；web-first expect 会等待
        # 客户端路由和异步渲染完成。
        expect(self.employee_information_heading).to_be_visible()

    def open_add_employee(self):
        # 实际 accessible name 含图标字符，role + 业务词比图标或 CSS 更稳定。
        self.page.get_by_role("button", name="Add").click()
        expect(self.add_employee_heading).to_be_visible()

    def create_employee(self, employee_data):
        self.first_name_input.fill(employee_data["firstName"])
        self.last_name_input.fill(employee_data["lastName"])
        self.employee_id_input.fill(employee_data["employeeId"])
        self.page.get_by_role("button", name="Save", exact=True).click()

    def search_by_employee_id(self, employee_id):
        self.employee_id_input.fill(employee_id)
        self.page.get_by_role("button", name="Search", exact=True).click()

    def result_row(self, employee_id):
        return self.page.get_by_role("row").filter(has_text=employee_id)
