# OrangeHRM Quality Lab Roadmap

> 基于 OrangeHRM 构建一个完整的测试开发实践项目。  
> 项目路线：功能测试 → 接口自动化 → 数据库 → UI 自动化 → 工程化 → CI → AI 辅助测试 → 简历 / 面试。

---

## 项目整体进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| Phase 0 | 项目初始化 | ✅ 已完成 |
| Phase 1 | 业务分析与手工测试设计 | ✅ 已完成 |
| Phase 2 | HTTP 与 Postman 接口测试 | ✅ 已完成 |
| Phase 3 | Requests 接口自动化 | ✅ 已完成 |
| Phase 4 | Pytest 工程化 | ✅ 已完成 |
| Phase 5 | 测试数据管理 | ✅ 已完成 |
| Phase 6 | Docker 本地测试环境 | ✅ 已完成 |
| Phase 7 | MySQL 数据库校验 | ✅ 已完成 |
| Phase 8 | Playwright UI 自动化 | ✅ 已完成 |
| Phase 9 | Allure 测试报告 | ✅ 已完成 |
| Phase 10 | Git 分支与 Pull Request | 🟡 进行中（等待 push / PR / CI / merge） |
| Phase 11 | GitHub Actions 持续集成 | 🟡 进行中（等待远端 CI 验证） |
| Phase 12 | Codex 代码变更影响分析 | ⬜ 未开始 |
| Phase 13 | AI 辅助失败分析（可选） | ⬜ 未开始 |
| Phase 14 | README 与 GitHub 项目整理 | ⬜ 未开始 |
| Phase 15 | 简历项目经历整理 | ⬜ 未开始 |
| Phase 16 | 项目面试复盘 | ⬜ 未开始 |

---

# Phase 0｜项目初始化 ✅

## 目标

建立一个能够正常开发、运行测试并使用 Git 管理的 Python 测试项目。

## 已完成

- [x] 安装并使用 Python 3.12
- [x] 创建项目级 `.venv`
- [x] 安装 Pytest
- [x] 创建 `requirements.txt`
- [x] 创建 `.gitignore`
- [x] 创建 `pytest.ini`
- [x] 创建最小环境测试
- [x] 成功执行 `pytest`
- [x] 初始化 Git 仓库
- [x] 完成第一次 commit
- [x] 创建 GitHub 仓库
- [x] 完成第一次 push

## 已掌握

```text
Working Directory
        ↓
     git add
        ↓
Staging Area
        ↓
   git commit
        ↓
Local Repository
        ↓
    git push
        ↓
GitHub
```

# Phase 1｜业务分析与手工测试设计 ✅
## 目标

在开始自动化之前，先理解 OrangeHRM 的核心业务。

## 重点模块
- Login
- PIM
- Admin
- Leave
- My Info

## 核心业务流程
### 员工管理
Admin 登录
   ↓
创建员工
   ↓
查询员工
   ↓
查看 / 修改员工

### 请假流程
员工申请请假
     ↓
管理员审批
     ↓
请假状态发生变化

## 需要完成
- [x] 熟悉 Login 模块
- [x] 熟悉 PIM 模块
- [x] 熟悉 Admin 模块
- [x] 熟悉 Leave 模块
- [x] 熟悉 My Info 模块
- [x] 创建 docs/business_notes.md
- [x] 创建 docs/test_points.md
- [x] 完成 Login 第一版测试点
- [x] 完成 Add Employee 第一版测试点

## 重点测试思维
- 正常流程
- 异常场景
- 边界值
- 状态流转
- 用户权限
- 数据一致性

## 验收标准
能够脱离文档说明：
- OrangeHRM 是什么系统；
- PIM 模块主要负责什么；
- 员工创建流程是什么；
- 请假审批流程是什么；
- 登录和新增员工应该如何设计测试点。

---

# Phase 2｜HTTP + Postman 接口测试 ✅
## 目标

从“页面操作”进入“接口测试”。

## 学习内容
- URL
- HTTP Method
- Headers
- Query Params
- Request Body
- Cookie
- Token
- Response
- Status Code
- JSON

## 实践任务
- [x] 使用浏览器 DevTools 观察 Employee Search 请求
- [x] 识别 URL、Method、Params、Headers、Cookie、Status 和 JSON Response
- [x] 确认登录页、登录提交和 Employee Search 的真实请求结构
- [x] 使用 Postman Cookie Jar 维护 Session Cookie
- [x] 从登录页动态提取 CSRF Token，并通过 Collection Variable 传递
- [x] 完成 `GET Login Page → POST Login` 认证链路
- [x] 动态生成 Employee ID，创建员工并保存响应数据
- [x] 查询刚创建的员工并验证关键字段一致
- [x] 使用 Collection Runner 按顺序执行完整请求链，8 个断言全部通过
- [x] 清除认证 Session 后直接查询员工，确认返回 `401 Unauthorized`

## 常见状态码
- 200  请求成功
- 201  创建成功
- 400  请求参数错误
- 401  未认证
- 403  无权限
- 404  资源不存在

## 验收标准
能够从一次页面操作说明：前端发送了什么 HTTP 请求，后端返回了什么响应。

## 实际验收结果

```text
GET Login Page
      ↓
POST Login
      ↓
POST Add Employee
      ↓
GET Search Employee
```

- 正向链路通过：4 个请求按顺序执行，8 个断言全部通过；
- 测试数据不依赖公共 Demo 的固定员工，创建成功后动态传递 `employeeId`；
- 未认证验证通过：清除 Session 后直接请求 Employee Search，实际返回 `401 Unauthorized`；
- 未认证响应体：`{"error":{"status":401,"message":"Session expired"}}`。

---

# Phase 3｜Python Requests 接口自动化 ✅
## 目标

使用 Python 将 Postman 中的接口测试转为自动化测试。

## 计划目录
```text
api/
├── auth_api.py
├── employee_api.py
└── leave_api.py

tests/
└── api/
```

## 学习内容

- requests.get
- requests.post
- requests.put
- requests.delete
- requests.Session
- Response
- JSON
- Assertion
- 认证会话管理
- API Client 基础封装

## 实践任务

- [x] 使用 Requests 编写第一个 GET 请求
- [x] 理解 Response、status_code、text 和 json()
- [x] 编写基础接口断言
- [x] 使用 requests.Session 跑通 OrangeHRM 登录
- [x] 使用 Python 完成员工创建和查询
- [x] 完成员工修改和删除，形成基础 CRUD 链路
- [x] 补充未认证访问 Employee Search 返回 401 的异常场景
- [x] 在出现明显重复代码后，完成 Employee API Client 基础封装
---

# Phase 4｜Pytest 工程化 ✅
## 目标

使用 Pytest 管理测试前置、测试数据和测试分类。

## 学习内容

- [x] fixture
- [x] conftest.py
- [x] fixture scope
- [x] parametrize
- [x] marker
- [x] setup / teardown

## 已完成实践

- [x] 将 Requests 一条龙脚本拆分为职责清晰的 Pytest 测试
- [x] 使用 `conftest.py` 管理共享前置条件和测试数据清理
- [x] 使用 session scope 复用登录 Session 和 Employee API Client
- [x] 使用 function scope 为每条员工测试创建独立数据
- [x] 使用 `yield` 组织 setup / teardown，断言失败时仍执行清理
- [x] 通过环境变量传入账号、密码和可选运行地址
- [x] 使用 `parametrize` 覆盖多组输入
- [x] 使用 marker 管理测试分类

## 重点问题
需要能够解释：
- 为什么要使用 fixture？
- 为什么登录 Session / 认证会话适合使用 session scope？
- 为什么测试数据适合使用参数化？

## 实际验收结果

- `python -m pytest tests/api -v`：`8 passed`，`0 failed`，`0 skipped`；
- `python -m pytest -m smoke -v`：`3 passed`，`0 failed`，`0 skipped`，`6 deselected`；
- `python -m pytest -m regression -v`：`8 passed`，`0 failed`，`0 skipped`，`1 deselected`。

---

# Phase 5｜测试数据管理 ✅
## 目标

避免自动化测试大量使用写死的数据。

## 本轮已实现

- [x] 使用时间戳动态生成 Employee ID
- [x] 使用 Faker 生成限制为 ASCII 字母的测试姓名
- [x] 使用 JSON 保存已经真实确认的必填字段异常 case
- [x] 使用函数式测试数据 Factory 生成合法基础 payload 并支持 `**overrides` 字段覆盖
- [x] 使用外部 JSON 数据和 `pytest.mark.parametrize` 完成基础数据驱动测试

## 实践内容
例如：由时间戳生成 10 位数字 Employee ID，并在当前 Python 进程内避免重复。

避免：
- Tom
- Tom2
- test123

## 重点理解
测试数据与测试逻辑分离。

## 最终验收结果

- `python -m pytest tests/api -v`：`8 passed`，`0 failed`，`0 skipped`；
- `python -m pytest -m smoke -v`：`3 passed`，`0 failed`，`0 skipped`，`6 deselected`；
- `python -m pytest -m regression -v`：`8 passed`，`0 failed`，`0 skipped`，`1 deselected`；
- Faker、函数式 Factory、JSON 参数化 case、Employee CRUD 和 cleanup 均在官方公共 Demo 上完成真实验证。

---

# Phase 6｜Docker 本地部署 OrangeHRM ✅
## 目标

解决公共 Demo 数据不稳定、无法直接控制数据库的问题。

## 环境
```text
OrangeHRM
     ↕
MySQL / MariaDB
```

## 学习内容
- Image
- Container
- Port
- Volume
- Docker Compose

## 已完成实践

- [x] 核验并使用 OrangeHRM 官方 image `orangehrm/orangehrm:5.9`
- [x] 使用 Docker Official Image `mariadb:10.11.19`
- [x] 使用 Compose 管理 OrangeHRM 与 MariaDB 两个服务
- [x] 使用 MariaDB healthcheck 和 `depends_on` 管理启动依赖
- [x] 配置 `localhost:8080` 到 OrangeHRM 容器 `80` 端口的映射
- [x] 使用独立 named volume 持久化数据库与 OrangeHRM 安装状态
- [x] 完成 OrangeHRM 首次初始化并创建本地管理员
- [x] 实际访问本地登录页并验证数据库连接
- [x] 完成不带 `-v` 的 Compose down/up 恢复验证
- [x] 使用现有环境变量切换机制在本地执行 smoke 测试

## 常用命令
- docker ps
- docker compose up -d
- docker compose down
- docker logs

## 验收标准
能够解释：为什么项目需要 Docker，而不是只说“我会 Docker”。

## 实际验收结果

- Docker Engine `29.7.2`、Docker Compose `v5.5.1` 实际可用；
- `docker compose config --quiet` 校验通过；
- MariaDB 容器保持 healthy，专用数据库用户连接检查返回 `mysqld is alive`；
- `http://localhost:8080` 实际返回 `200` 并进入 OrangeHRM 登录页；
- `orangehrm_quality_lab_db_data` 与 `orangehrm_quality_lab_app_data` 已实际创建；
- `docker compose down` 后两个 volume 保留，重新 `up -d` 后仍直接进入登录页；
- 重启前、重启后分别执行本地 smoke，均为 `3 passed`、`6 deselected`；
- Phase 6 收口时尚未新增数据库测试、PyMySQL 或 DB fixture；这些内容在下方 Phase 7 中完成。

---

# Phase 7｜MySQL 数据库校验 ✅
## 目标

在接口响应校验之外，进一步验证数据库最终状态。

## 示例
```text
POST 创建员工
      ↓
接口返回 empNumber
      ↓
查询数据库
      ↓
确认员工记录真实存在
```

## 已完成实践

- [x] 将 MariaDB 宿主机端口仅绑定到 `127.0.0.1`，默认使用 `3307`；OrangeHRM 容器仍通过 `db:3306` 连接数据库
- [x] 使用 PyMySQL 从 Windows 宿主机连接 MariaDB，并通过环境变量读取连接配置
- [x] 在 `utils/db.py` 实现最小连接和 `fetch_one` 查询层，使用 `DictCursor`、参数化 SQL 和明确的资源关闭
- [x] 实际确认 OrangeHRM 5.9 使用 `hs_hr_employee`，并核验员工主键、Employee ID 和三个姓名字段
- [x] 使用 `emp_number` 精确查询同一记录，完成 Create / Update / Delete 的 API Response Assertion + Database State Assertion
- [x] 建立独立 `db` marker 和本地环境守卫，不让数据库测试依赖或混用官方公共 Demo
- [x] `SELECT` / `WHERE` 进入自动化断言；`COUNT` / `ORDER BY` / `JOIN` 在本地数据库实际练习，未为打卡增加业务测试

## 实际目录

```text
utils/
└── db.py

tests/
└── db/
    ├── conftest.py
    └── test_employee_db.py
```

## 重点理解

- API 响应成功只能证明接口返回了成功结果；数据库查询进一步确认最终持久化状态；
- 数据库测试中的 `SELECT` 是 Assert，业务数据创建、修改、删除和 cleanup 仍通过现有 API 完成；
- SQL 只用 `WHERE emp_number = %s` 定位唯一记录，字段差异由 Python 逐项断言，失败信息更容易定位。

## 实际验收结果

- `docker compose config --quiet` 校验通过；
- MariaDB 保持 healthy，端口为 `127.0.0.1:3307->3306/tcp`，OrangeHRM 正常运行；
- 宿主机 PyMySQL 实连 MariaDB `10.11.19` 成功，确认 `hs_hr_employee` 的 5 个目标字段；
- `python -m pytest tests/db -v`：`3 passed`；
- `python -m pytest tests/api -v`：`8 passed`；
- `python -m pytest -m smoke -v`：`3 passed`，`9 deselected`；
- 本地环境执行完整测试集合：`12 passed`。

---

# Phase 8｜Playwright UI 自动化 ✅
## 目标

对少量关键业务流程进行 Web UI 冒烟自动化。

## 已完成场景

- [x] 使用有效管理员凭证登录并进入 Dashboard
- [x] 使用错误密码登录并显示 `Invalid credentials`
- [x] 通过 UI 创建动态员工，并在 Personal Details 回显姓名与 Employee ID
- [x] 通过现有 API fixture 创建员工，再通过 UI 按 Employee ID 查询唯一结果
- [x] 查询未创建的动态 Employee ID，并显示空结果且无员工数据行

请假核心流程本阶段 deferred。完整状态流转需要新增独立 ESS 账号、登录用户与员工关联、假期类型、假期额度、有效日期以及 Admin 审批后的 ESS 回查；当前仓库没有对应 Leave API / fixture。为了保持 UI smoke 小而稳定，本阶段不为凑数量扩展这些前置。

## 学习内容

- [x] Locator
- [x] Playwright 自动等待与 web-first assertion
- [x] 失败 Screenshot
- [x] 失败 Trace
- [x] 简单 Page Object

## 实际目录

```text
pages/
├── login_page.py
└── employee_page.py

tests/
└── ui/
    ├── conftest.py
    ├── test_login_ui.py
    └── test_employee_ui.py
```

## 关键设计

- Locator 优先使用 `get_by_role`、`get_by_placeholder` 和动态业务文本；OrangeHRM 标签未关联 input 时，才按包含 `Employee Id` 的局部表单组缩小范围；没有固定 sleep、XPath 或 `nth()` 定位；
- 依靠 `fill`、`click` 的 actionability 自动等待，以及 `expect` 的重试等待页面跳转、异步列表和可见反馈；
- 先以内联 Locator 跑通最小登录和员工链路，确认登录与 PIM 行为真实重复后，才提取 `LoginPage` 和 `EmployeePage`；没有增加 BasePage、多层 driver 或通用框架；
- UI Create 使用现有 Factory 生成数据，并在 `yield` 后通过现有 Employee API 精确查询和删除；UI Search 直接复用 `created_employee` 完成 API Arrange / Cleanup；
- `pytest.ini` 配置 `--screenshot=only-on-failure`、`--tracing=retain-on-failure` 和全页截图；失败产物位于 `test-results/` 并被 Git 忽略。Trace 可能包含页面输入、Cookie 和网络信息，只用于本地排查；
- 本地最终验收使用已经真实通过的系统 Chrome channel：`--browser-channel chrome`。浏览器二进制安装问题不与业务测试结果混为一谈。

## 实际验收结果

- Page Object 重构前基线：`5 passed`；
- Page Object 重构后：`5 passed`；
- 最终连续稳定性验证第一轮：`5 passed in 38.15s`；
- 最终连续稳定性验证第二轮：`5 passed in 36.53s`；
- 原有 API + DB 关键回归：`11 passed in 3.75s`；
- 使用 Chrome channel 执行本地完整集合：`17 passed in 37.60s`；
- 失败 Screenshot / Trace 已在真实 Locator 失败中生成并用于修复，成功运行后按 failure-only 策略不保留产物；
- 连续两轮 UI 验收未发现 flaky，也未发现跨用例状态污染。

接口自动化继续负责主要业务验证，UI 自动化只覆盖核心用户链路。

---

# Phase 9｜Allure 测试报告 ✅
## 目标

提高测试执行结果和失败信息的可读性。

## 已完成实践

- [x] 增加 `allure-pytest==2.16.0`，让 Pytest 执行结果、业务标签、步骤和附件写入 `allure-results/`
- [x] 确认本机已有可用的 Allure CLI `2.38.1` 和 Java `11.0.2`，没有重复安装系统工具
- [x] 在 `pytest.ini` 默认配置 `--alluredir=allure-results` 和 `--clean-alluredir`，每次执行只保留当前测试会话的原始结果
- [x] 使用 Allure CLI 将原始结果生成到 `allure-report/`，并通过本地报告服务实际读取页面
- [x] 只为 API、DB、UI 各一条代表场景增加业务标签、风险等级和关键步骤，没有机械装饰全部测试
- [x] 将 Create Employee API 响应和员工数据库实际行作为 JSON 附件
- [x] 将 pytest-playwright 已有的失败 Screenshot / Trace 附加到对应 Allure 用例，同时继续在 `test-results/` 保留原始产物
- [x] 确认 `allure-results/`、`allure-report/` 和 `test-results/` 均被 Git 忽略

## 关键设计

- `allure-pytest` 是测试框架适配器，负责把 Pytest 运行过程写成原始结果；Allure CLI 是独立渲染工具，负责把这些结果生成可查看的 HTML 报告；
- Feature / Story 按业务组织：员工接口创建是 `PIM / Employee Management`，数据库持久化校验是 `PIM / Employee Data Consistency`，管理员 UI 登录是 `Authentication / Administrator Login`；没有使用 API / DB / UI 文件夹名作为业务层级；
- Severity 按业务失败影响标记：员工创建和数据一致性为 `critical`，阻断所有受保护功能的管理员登录为 `blocker`；
- Step 只覆盖提交业务动作、核对核心结果等诊断边界，没有把每个请求、fill、click 或单条 assert 拆成步骤；
- API Response 和 DB Row 直接附为 JSON。UI 失败附件复用 pytest-playwright 的 `output_path`：浏览器上下文 teardown 完成后，再把已落盘的 Screenshot 和 Trace 复制进 Allure；
- `test-results/` 是 Playwright 原始失败诊断，`allure-results/` 是可重新生成报告的原始 Allure 数据，`allure-report/` 是 CLI 生成的静态网页。Trace 和两类 Allure 目录可能包含业务数据、Cookie 或网络信息，只作为本地临时产物；
- `--clean-alluredir` 防止不同测试会话的结果混在同一份本地报告中。Phase 11 已选择只保存原始结果 artifact，不在当前阶段安装 Allure CLI、发布 Pages 或维护历史趋势。

## 实际验收结果

- `python -m pytest tests/api -v`：`8 passed in 3.54s`；
- `python -m pytest tests/db -v`：`3 passed in 1.73s`；
- 使用 Chrome channel 执行 UI：`5 passed in 38.55s`；
- 使用 Chrome channel 执行本地完整集合：`17 passed in 39.84s`；最终 `allure-results/` 恰好包含 `17` 条结果，状态全部为 passed；
- 临时受控 UI 失败真实生成 `test-failed-1.png` 和 `trace.zip`，两者均成功复制为该失败用例的 Allure attachment；验证后已删除临时用例，完整回归重新清理了失败结果和 Playwright 失败产物；
- `allure generate allure-results --clean -o allure-report` 返回成功，生成报告摘要为 `17 total / 17 passed`；
- `allure open -h 127.0.0.1 -p 59032 allure-report` 启动本地报告服务，实际请求首页返回 `HTTP 200`；
- `pip check` 返回 `No broken requirements found`。

---

# Phase 10｜Git 分支与 Pull Request 🚧
## 目标

模拟实际团队 Git 协作流程。

## 本轮演练

```text
main
  ↑ Pull Request + CI
feat/github-actions-ci
```

Phase 11 的 workflow 与文档修改就是本次 Branch → Pull Request → Merge 的真实变更内容，不额外制造演示提交。

## 当前状态

- [x] 已在 `feat/github-actions-ci` 分支完成本地实现与验证
- [ ] 用户本人检查并 commit
- [ ] 用户本人 push feature branch
- [ ] 创建 Pull Request，并观察 PR trigger 的 CI
- [ ] CI 通过后由用户本人 merge
- [ ] 确认 merge 后 `main` 的 push trigger 再次执行

在上述远端协作链完成前，Phase 10 保持进行中。

---

# Phase 11｜GitHub Actions CI 🚧
## 目标

实现代码提交后自动执行测试。

## 当前 CI 架构

```text
Pull Request → main ─┐
                     ├→ ubuntu-24.04 单一 job
Push → main ─────────┘        ↓
                    Checkout + Python 3.12
                              ↓
                    requirements + Chromium
                              ↓
                    OrangeHRM + MariaDB
                              ↓
                    首次初始化与真实就绪检查
                              ↓
                    单次执行完整 17 条测试
                              ↓
                    短期 artifact + 环境清理
```

## GitHub Actions 概念在本项目中的对应关系

| 概念 | 本项目中的含义 |
|---|---|
| workflow | `.github/workflows/test.yml` 定义的一整套自动验证流程 |
| trigger | 面向 `main` 的 Pull Request 和 `main` 收到 push 时启动流程 |
| job | `integration-tests`，在同一台干净 runner 上共享容器和测试产物 |
| runner | 显式使用 GitHub-hosted `ubuntu-24.04` |
| step | Checkout、安装依赖、启动服务、初始化、测试、诊断、上传与清理等顺序动作 |
| uses | 调用 `checkout`、`setup-python`、`upload-artifact` 这些可复用 action |
| run | 在 runner 上执行 pip、Playwright、Docker Compose、curl 和 pytest 命令 |

## 已完成的本地实现

- [x] 创建 `.github/workflows/test.yml`
- [x] PR 只监听目标分支 `main`，用于 merge 前验证
- [x] push 只监听 `main`，用于 merge 后验证，并避免 feature push 与 PR 重复执行
- [x] 权限缩小为 `contents: read`，Checkout 后不持久化凭证，并且不使用 `pull_request_target`
- [x] 每次 job 动态生成并遮罩一次性数据库和管理员密码，不读取 `.env`，不依赖 Repository Secrets
- [x] 使用 MariaDB healthcheck、installer HTTP 和最终登录 URL 判断就绪，固定 sleep 只作为条件轮询间隔
- [x] 使用 OrangeHRM 5.9 镜像内的 YAML 兼容安装入口完成空数据库初始化，并确认临时明文配置在成功后被删除
- [x] 显式安装 Playwright bundled Chromium，在 CI 中使用 `--browser chromium`，不改变本地 `--browser-channel chrome`
- [x] 单次运行完整测试，保留同一会话的全部 `allure-results`
- [x] 生成 JUnit XML 并额外要求 skip 数为 0，同时核对 Allure 结果数量与状态，防止环境漏配或结果缺失后仍显示绿色
- [x] 失败时输出限量 Compose 状态与日志，不展开 Compose 配置或环境变量
- [x] 将 Allure 原始结果保存 3 天；UI 失败截图与 Trace 已由现有 fixture 附入同一结果，取消运行时不继续上传
- [x] 无论成功失败都删除 runner 内的容器、网络和 volumes

## OrangeHRM 5.9 首次初始化结论

新版 `installer/console install:on-existing-database` 的帮助中虽然存在 Symfony 通用的 `--no-interaction`，但命令实现会明确拒绝非交互模式。CI 没有使用 `expect` 或按提示顺序喂答案。

固定的 5.9 镜像仍保留 `installer/cli_install.php`：它读取 `cli_install_config.yaml`，可在无人工输入时完成迁移、管理员创建和配置写入，并在成功后删除包含明文凭证的 YAML。该入口已被上游标记 deprecated，因此这是当前固定版本的兼容方案，不是可跨版本保证的公共接口；未来升级 OrangeHRM 必须重新验证或替换初始化方式。

## 本地真实验证结果

- 使用与现有本地环境完全不同的容器、网络、volumes 和端口，从空 MariaDB 开始验证；
- MariaDB health 通过，首次 installer HTTP 可达；
- 临时 `cli_install_config.yaml` 创建后的实际 mode 为 `600`；
- 旧 CLI / YAML 在无人工输入下完成初始化并删除临时配置；
- 最终 URL 为 `/web/index.php/auth/login`，不再进入 installer；
- 新建管理员完成真实 Session 登录；
- `hs_hr_employee` 表存在；
- 使用 Playwright bundled Chromium 单次执行完整集合：`17 passed in 38.17s`，`skipped=0`；
- `allure-results/` 包含 `17` 条结果，状态全部为 passed；
- 验证结束后只删除了本次临时 Docker 资源，原有本地 volumes 未受影响；
- `actionlint 1.7.12` 对 workflow 的 Actions 语法与内嵌 shell 检查通过。

## 等待远端 GitHub Actions 验证

- [ ] PR trigger 在 GitHub 上真实启动
- [ ] `actions/checkout@v7`、`actions/setup-python@v7`、`actions/upload-artifact@v7` 在 hosted runner 上执行
- [ ] Ubuntu runner 完成镜像、Python 依赖和 Chromium 下载
- [ ] Linux runner 从空环境完成 OrangeHRM 初始化及 17 条完整测试
- [ ] artifact 实际上传，并应用 3 天保留期
- [ ] merge 后 `main` push trigger 再次通过

Phase 11 只有远端 workflow 实际成功后才能标记完成。

## 已知风险与权衡

- YAML 兼容安装入口已被 OrangeHRM 标记 deprecated；固定 5.9 版本降低了当前变化面，但升级时必须重新验证；
- Compose image 使用版本 tag 而非 digest，`requirements.txt` 也只固定直接依赖，没有达到镜像 digest + 全量 hash lock 的最高复现级别；
- GitHub 官方 actions 使用当前 v7 major tag，便于接收同 major 修复，但不如完整 commit SHA 不可变；
- hosted runner 仍需访问 Docker Hub、PyPI 和 Playwright CDN，外部下载故障会让 CI 失败；
- Requests 调用尚未逐个设置 timeout，因此 workflow 同时设置 15 分钟测试 step 上限和 30 分钟 job 上限，避免无限占用 runner；
- CI 只保存可重新渲染的 Allure 原始结果，不额外安装 Java / Allure CLI；代价是 Actions 页面不能直接浏览完整 HTML 报告。

## 项目文件

```text
.github/
└── workflows/
    └── test.yml
```

## 重点理解
CI 的核心不是某一个工具。核心是：代码发生变化以后，自动完成测试验证。

---

# Phase 12｜Codex 代码变更影响分析
## 目标

实践 AI 辅助测试中的“需求 / 代码变更影响分析”。

## 流程
```text
代码发生修改
     ↓
读取 git diff
     ↓
分析修改的方法 / 模块
     ↓
搜索调用和引用关系
     ↓
寻找已有测试
     ↓
输出潜在影响范围
     ↓
测试人员确认回归范围
```

## 项目文件
```text
AGENTS.md

skills/
└── change-impact-analysis/
    └── SKILL.md
```

## 原则
AI 只负责：
- 检索；
- 分析；
- 提示风险。

测试人员负责：
- 判断业务；
- 设计测试；
- 实际验证；
- 确认 Bug。

---

# Phase 13｜AI 辅助失败分析（可选）
## 输入
- Pytest Failure
- Stack Trace
- 接口 Response
- 相关日志

## 输出
- 失败原因候选
- 相关代码位置
- 建议排查方向
- 需要人工确认的内容

该阶段属于加分项，不影响主体项目完成。

---

# Phase 14｜README 与 GitHub 项目整理
## 最终 README 计划包含
- 项目背景
- 被测系统
- 技术栈
- 测试策略
- 项目目录
- API 自动化
- 数据库校验
- UI 自动化
- CI
- AI 辅助测试
- 项目运行方式
- 测试报告截图

---

# Phase 15｜简历项目经历
项目完成后再根据真实成果编写简历。

预计方向：**OrangeHRM 人力资源管理系统自动化测试**

可能涉及：
- Python
- Pytest
- Requests
- Playwright
- MySQL
- Docker
- Allure
- GitHub Actions
- Codex

只有实际完成并能够解释的技术才写入简历。

---

# Phase 16｜项目面试复盘
## 最终需要准备
### 项目介绍
- 1 分钟版本
- 3 分钟版本

### 高频问题
- 为什么接口自动化优先于 UI 自动化？
- fixture 为什么这样设计？
- 如何管理测试数据？
- 如何避免用例数据污染？
- 为什么需要数据库校验？
- Docker 在项目中解决了什么问题？
- Selenium 和 Playwright 有什么区别？
- CI 流程是怎么运行的？
- GitHub Actions 和 Jenkins 有什么关系？
- AI 如何做代码影响分析？
- 为什么 AI 输出不能直接作为 Bug？

## 最终目标
完成项目以后，应能够形成以下能力链：

业务分析
   ↓
测试设计
   ↓
接口测试
   ↓
接口自动化
   ↓
数据库验证
   ↓
UI 自动化
   ↓
测试工程化
   ↓
持续集成
   ↓
AI 辅助测试
   ↓
项目表达 / 面试

最终要求：不仅项目能运行，而且项目中的主要设计和技术都能够自己解释。
