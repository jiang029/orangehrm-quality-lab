# OrangeHRM 业务梳理

## 1. 系统定位

OrangeHRM 是人力资源管理系统。

当前重点关注模块：

- Admin
- PIM
- Leave
- My Info

---

## 2. 用户角色

### Admin

观察到的权限：

- 员工信息管理
- 系统用户管理
- ...

### Employee / ESS

暂未完整验证。

---

## 3. PIM - Employee Management

### Add Employee

前置条件：

- Admin 已登录

主要输入：

- First Name
- Middle Name
- Last Name
- Employee ID
- ...

执行成功后：

- 创建员工
- 可以进入员工详情
- 可以在 Employee List 查询

### Employee List

支持的查询条件：

- Employee Name
- Employee ID
- ...

---

## 4. 核心业务流程

### Flow 1：创建员工

Admin Login
→ PIM
→ Add Employee
→ 输入员工信息
→ Save
→ Employee Detail
→ Employee List Search

### 当前想到的风险

- 必填项为空
- Employee ID 重复
- 姓名长度边界
- 特殊字符
- 创建后搜索不到
- 保存数据与详情页不一致