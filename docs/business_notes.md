# OrangeHRM 业务梳理

## 1. 本阶段的学习范围

OrangeHRM 是一个人力资源管理系统（HRM，Human Resource Management）。

本项目当前只学习后续测试会用到的基础功能：

- Login：用户登录和退出；
- Dashboard：登录后的首页；
- PIM：员工档案管理；
- Admin：系统用户和角色管理；
- Leave：请假申请与管理；
- My Info：当前登录员工查看自己的资料。

本次观察环境为 OrangeHRM OS 5.9 官方公开演示环境。公开环境中的数据会被其他使用者修改或重置，因此页面数据不适合作为固定测试数据。

---

## 2. 常用英文菜单对照

| 英文 | 中文理解 | 主要用途 |
|---|---|---|
| Login | 登录 | 验证用户身份并进入系统 |
| Dashboard | 仪表盘 / 首页 | 展示常用入口、待办和概览信息 |
| Admin | 系统管理 | 管理登录账号、角色、状态及基础配置 |
| PIM | 人事信息管理 | 管理所有员工的人事档案 |
| Employee List | 员工列表 | 查询和查看员工 |
| Add Employee | 新增员工 | 创建员工档案，可选择同时创建登录账号 |
| Leave | 请假管理 | 申请、查询、分配和审批请假 |
| My Info | 我的信息 | 查看或维护当前登录员工自己的资料 |
| ESS | 员工自助角色 | 员工处理自己的资料、请假等事务 |

---

## 3. 用户角色与核心数据关系

### Admin

Admin 是管理员角色。当前观察到它可以进入 Admin、PIM、Leave、My Info 等模块，能够管理系统用户、员工档案和请假记录。

### Employee / ESS

Employee 表示公司中的员工；ESS（Employee Self Service）表示员工自助登录角色。

ESS 的详细权限尚未使用独立账号完整验证。根据当前页面结构，它主要用于处理与本人有关的资料和请假业务，不能直接假设拥有 Admin 的全员管理权限。

### 员工档案与登录账号不是同一个对象

- 员工档案由 PIM 管理，保存姓名、Employee ID、联系方式、职位等人事信息；
- 登录账号由 Admin 的 System Users 管理，包含 Username、User Role 和 Status；
- 一个员工可以先只有员工档案，不一定能够登录系统；
- 创建员工时打开 `Create Login Details`，可以同时为该员工创建登录账号；
- 登录账号需要关联员工，并设置 Admin 或 ESS 角色及 Enabled / Disabled 状态。

这个区别很重要：Employee ID 是员工编号，Username 是登录名，两者不能混为一谈。

---

## 4. Login - 登录与退出

### 业务目的

登录用于确认操作者身份，并根据账号角色允许用户访问相应功能。未登录用户不应该直接访问员工列表等内部页面。

### 页面元素

- Username：用户名；
- Password：密码；
- Login：提交登录；
- Forgot your password?：忘记密码入口。

### 登录步骤

1. 打开 OrangeHRM 登录页；
2. 在 Username 输入用户名；
3. 在 Password 输入密码；
4. 点击 Login；
5. 身份验证成功后进入 Dashboard。

### 本次观察结果

- 使用演示页公开提供的管理员账号可以成功登录；
- 登录成功后进入 Dashboard，并显示当前用户名称和其可访问的左侧菜单；
- 点击右上角用户名称会出现 About、Support、Change Password 和 Logout；
- 点击 Logout 后返回登录页；
- 退出后直接访问 Employee List，系统会重定向到登录页。

这说明系统不仅在页面上隐藏菜单，还会检查用户是否处于登录状态。

---

## 5. Dashboard - 登录后的首页

Dashboard 是登录成功后的首页，用来展示概览信息和常用操作入口。

当前观察到的内容包括：

- Time at Work：工作时间概览；
- My Actions：当前用户的待办事项；
- Quick Launch：常用功能快捷入口；
- Employees on Leave Today：今日请假员工；
- Employee Distribution：员工分布统计。

Dashboard 不是本项目当前的重点测试模块。它主要用于确认登录成功，以及帮助用户快速进入常用业务。

---

## 6. PIM - 员工档案管理

PIM 是 Personnel Information Management 的缩写，可以理解为“人事信息管理”。它主要管理公司员工的人事档案。

### Employee List - 员工列表

操作路径：

```text
登录 → PIM → Employee List
```

当前观察到的查询条件：

- Employee Name：员工姓名；
- Employee Id：员工编号；
- Employment Status：雇佣状态；
- Include：是否包含离职员工；
- Supervisor Name：直属主管姓名；
- Job Title：职位；
- Sub Unit：所属部门。

页面提供 Search 查询、Reset 重置和 Add 新增员工。

### Add Employee - 新增员工

操作路径：

```text
Admin 登录 → PIM → Employee List → Add
```

创建员工的基础步骤：

1. 进入 Add Employee 页面；
2. 输入 First Name（名字）；
3. 根据需要输入 Middle Name（中间名）；
4. 输入 Last Name（姓氏）；
5. 检查或修改系统默认生成的 Employee Id；
6. 根据需要上传员工头像；
7. 如果员工需要登录，打开 Create Login Details 并填写账号信息；
8. 点击 Save 保存；
9. 保存成功后应进入该员工的详情页，并能够在 Employee List 中查询到该员工。

页面显示 First Name 和 Last Name 属于必填姓名信息，Middle Name 可选。头像支持 jpg、png、gif，页面提示文件上限为 1 MB，建议尺寸为 200 × 200。

打开 Create Login Details 后会增加：

- Username：登录用户名；
- Status：账号状态，可选 Enabled 或 Disabled；
- Password：登录密码；
- Confirm Password：确认密码。

本次为了避免污染公共演示环境，只观察了表单和操作路径，没有提交新的员工记录。因此，保存后的详情展示和查询结果仍需要在后续手工测试中实际验证。

---

## 7. Admin - 系统用户管理

Admin 模块不只是“管理员个人页面”，而是系统管理入口。本项目当前先关注其中的 User Management。

操作路径：

```text
Admin 登录 → Admin → User Management → System Users
```

System Users 页面当前支持按照以下条件查询登录账号：

- Username：登录用户名；
- User Role：用户角色，如 Admin、ESS；
- Employee Name：账号关联的员工；
- Status：账号状态，如 Enabled、Disabled。

列表会展示 Username、User Role、Employee Name 和 Status，并提供新增、编辑和删除操作。

业务上需要注意：

- Enabled 账号可以参与正常登录；
- Disabled 账号表示账号被停用；
- User Role 决定账号能够执行哪些操作；
- Employee Name 表明登录账号与员工档案存在关联。

Admin 模块还包含 Job、Organization、Qualifications、Nationalities、Configuration 等配置入口，当前阶段只需要知道它们属于系统基础配置，不展开学习。

---

## 8. Leave - 请假管理

Leave 模块同时包含员工自助和管理员处理两类功能。

### 员工视角

- Apply：提交自己的请假申请；
- My Leave：查看自己的请假记录和状态。

### 管理视角

- Leave List：查询员工请假记录；
- Assign Leave：管理员代员工分配请假；
- Entitlements：管理假期额度；
- Configure：管理假期类型等基础配置。

当前 Leave List 可以按照日期、请假状态、请假类型、员工姓名和部门等条件查询。列表关注 Date、Employee Name、Leave Type、Leave Balance、Number of Days 和 Status 等信息。

### 基础请假流程

```text
系统先配置假期类型和员工假期额度
        ↓
员工进入 Leave → Apply 提交申请
        ↓
管理员在 Leave List 查看并处理
        ↓
请假状态发生变化
        ↓
员工在 My Leave 查看处理结果
```

本次观察时，当前演示账号的 Apply Leave 页面显示 `No Leave Types with Leave Balance`，说明员工没有可用的假期类型或余额时，不能直接完成请假申请。

本次尚未实际提交和审批请假，因此具体状态名称、余额扣减时机以及不同角色权限仍需要后续验证。

---

## 9. My Info - 当前用户的个人资料

操作路径：

```text
登录 → My Info
```

My Info 只指向当前登录账号所关联员工的资料。当前观察到的资料分类包括：

- Personal Details：个人基本信息；
- Contact Details：联系方式；
- Emergency Contacts：紧急联系人；
- Dependents：家属；
- Immigration：证件 / 移民信息；
- Job：职位信息；
- Salary：薪资信息；
- Report-to：汇报关系；
- Qualifications：资质；
- Memberships：会员信息。

Personal Details 中包括姓名、Employee Id、其他编号、驾驶证、国籍、婚姻状态、出生日期、性别、自定义字段和附件等信息。

### My Info 与 PIM 的区别

- PIM 面向员工管理人员，用于查询和管理员工档案；
- My Info 面向当前登录用户，用于查看或维护自己的资料；
- 两者可能访问同一员工数据，但入口、可见范围和可修改权限不同。

ESS 用户在 My Info 中究竟可以修改哪些字段，当前尚未使用独立 ESS 账号验证，不能仅凭 Admin 页面推断。

---

## 10. 当前阶段的核心业务流程

### 流程一：用户登录

```text
输入 Username 和 Password
        ↓
系统验证账号、密码和账号状态
        ↓
验证成功后进入 Dashboard
        ↓
根据角色显示并允许访问对应功能
```

### 流程二：创建员工档案

```text
Admin 登录
    ↓
PIM → Add Employee
    ↓
填写员工基本信息
    ↓
可选：同时创建登录账号
    ↓
保存员工
    ↓
进入员工详情
    ↓
在 Employee List 查询员工
```

### 流程三：员工请假

```text
准备假期类型和员工余额
    ↓
员工申请请假
    ↓
管理员处理申请
    ↓
请假状态和余额发生变化
    ↓
员工查看结果
```

---

## 11. 尚待后续确认的内容

以下内容不能只根据页面名称下结论，需要在后续手工测试中验证：

- ESS 角色实际可以访问哪些菜单；
- 新增员工保存后的详情和查询结果；
- 重复 Employee Id 的实际处理方式；
- Disabled 账号的登录表现；
- 请假完整的申请、审批和状态流转；
- 请假余额在申请、审批或取消时如何变化；
- Admin 与 ESS 对同一员工资料的可修改范围。

这些未知项会成为后续测试设计中的风险候选，而不是直接当作系统 Bug。
