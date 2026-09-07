class EmployeeAPI:
    """封装员工接口请求，只返回 Response，不负责业务断言。"""

    def __init__(self, session, base_url):
        # 复用已登录 Session，让每个员工接口自动携带认证 Cookie。
        self.session = session
        self.employees_url = f"{base_url}/web/index.php/api/v2/pim/employees"

    def create_employee(self, employee_data):
        # json= 会把 Python 字典序列化为 JSON 请求体，并设置对应 Content-Type。
        return self.session.post(
            self.employees_url,
            json=employee_data,
        )

    def search_employee(self, employee_id):
        # params= 把 employeeId 编码到 URL 查询字符串；它是业务查询字段，
        # 与后端用于更新、删除记录的 empNumber 不是同一个标识。
        return self.session.get(
            self.employees_url,
            params={"employeeId": employee_id},
        )

    def update_personal_details(self, emp_number, personal_details):
        # empNumber 是后端员工主键，放在 URL 路径中定位需要修改的记录。
        personal_details_url = (
            f"{self.employees_url}/{emp_number}/personal-details"
        )
        # personal_details 是结构化字段，使用 json= 发送完整的 JSON 请求体。
        return self.session.put(
            personal_details_url,
            json=personal_details,
        )

    def delete_employee(self, emp_number):
        # 当前接口采用可批量删除的 ids 列表格式，即使本次只删除一名员工，
        # 也需要把单个 empNumber 放入列表后作为 JSON 请求体发送。
        return self.session.delete(
            self.employees_url,
            json={"ids": [emp_number]},
        )
