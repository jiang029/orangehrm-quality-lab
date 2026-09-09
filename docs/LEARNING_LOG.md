# OrangeHRM Quality Lab - Learning Log

> 用于记录项目学习过程中真正遇到的问题、解决方式和自己的理解。  
> 面试前可以通过该文档快速复习项目中的知识点和踩坑经历。

---

# 2026-09-05

## 1. Python 虚拟环境

### 遇到的问题

项目中同时出现：

```text
venv/
.venv/
```

PyCharm 的 Project Interpreter 已经选择 `.venv`，但是 Terminal 仍然激活旧的 `venv`。

导致：

- `pip install` 可能安装到错误环境；
- `pip freeze` 得到错误结果；
- PyCharm 和 Terminal 使用的 Python 不一致。

### 原因

PyCharm 中：

- Project Interpreter

和已经打开的：

- Terminal

并不是完全相同的东西。

修改 Project Interpreter 后，旧 Terminal 可能仍然保留之前激活的虚拟环境。

### 排查方法

查看当前 Python：

```bash
python -c "import sys; print(sys.executable)"
```

查看 pip 所属环境：

```bash
python -m pip --version
```

查看当前安装依赖：

```bash
python -m pip list
```

### 最终环境

项目统一使用：

```text
orangehrm-quality-lab/.venv
```

### 我的理解

`.venv` 和 `venv` 本质都是 Python 虚拟环境。

区别主要是目录名称和位置。

本项目采用：

```text
项目根目录/.venv
```

保证每个项目拥有独立 Python 依赖。

---

## 2. Git 基础流程

### 当前理解

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
GitHub Remote Repository
```

### 常用命令

查看状态：

```bash
git status
```

加入暂存区：

```bash
git add .
```

创建版本记录：

```bash
git commit -m "message"
```

上传 GitHub：

```bash
git push
```

查看提交历史：

```bash
git log --oneline
```

### 第一次 Commit

```text
chore: initialize test project
```

### 我的理解

`git add` 并不是正式保存版本，而是：

- 把准备提交的修改放进暂存区。

`git commit` 才会：

- 在本地 Git 仓库中生成一次正式版本记录。

`git push` 则是：

- 把本地已经提交的 Git 历史同步到 GitHub。

---

# 2026-09-06

## 3. Postman Session 认证与接口依赖链

### 遇到的问题

浏览器中的 Employee Search 可以成功，但最初在 Postman 中直接复制 Cookie 后返回：

```text
401 Unauthorized
Session expired
```

搭建完整请求链时还遇到过三个已解决的问题：

- 登录变量名拼写错误，`POST /auth/validate` 返回 `302`，但跳转位置是登录页而不是 Dashboard；
- Add Employee 误用了 `GET`，并把 `Accept`、`Content-Type` 放进 Params，导致 `422 Unprocessable Content`；
- Collection Runner 使用了已有登录状态，登录页响应中没有 CSRF Token，导致第一条提取断言失败，但后续请求因旧 Cookie 和旧变量而通过。

### 原因

OrangeHRM Web 登录不是一个可以脱离上下文单独调用的请求，而是一条 Session 依赖链：

```text
GET Login Page
      ↓ 获得匿名 Session Cookie 和 CSRF Token
POST Login
      ↓ 校验 Cookie、Token 和账号密码，建立认证 Session
Employee API
      ↓ 自动携带认证后的 Session Cookie
```

浏览器和 Postman 是两个独立客户端，各自维护 Cookie。只复制一个过期或与 CSRF Token 不匹配的浏览器 Cookie，不能建立可靠的 Postman 登录状态。

另外，HTTP 状态码必须结合响应头和响应体判断。登录成功和失败都可能返回 `302`：

- `Location` 指向 `/dashboard/index`：登录成功；
- `Location` 指向 `/auth/login`：登录失败。

### 排查过程

1. 使用浏览器 DevTools 的 Network 确认真实 URL、Method、Content-Type、Payload、Cookie 和 Response；
2. 对比登录请求的 `Location` 响应头，而不是只看 `302`；
3. 检查 Postman 中变量是否正确解析、Headers 是否误放进 Params、请求方法是否正确；
4. 清除旧 Cookie 和动态变量，从第一条请求重新执行；
5. 使用 Collection Runner 按 `01 → 02 → 03 → 04` 顺序运行，确认 8 个断言全部通过；
6. 使用不携带 Cookie 的独立请求复核未认证结果。

### 解决方式

最终完成以下 Postman 请求链：

```text
01 - Auth - Get Login Page
02 - Auth - Login
03 - PIM - Add Employee
04 - PIM - Search Employee
```

- Cookie Jar 自动接收和发送 Session Cookie，不手工维护浏览器 Cookie；
- 第一条请求从 HTML 动态提取 CSRF Token，并保存为 Collection Variable；
- 创建员工前动态生成 Employee ID；
- 创建成功后保存响应中的 `employeeId` 和 `empNumber`；
- 查询请求使用刚创建的 `employeeId`，验证创建与查询的关键字段一致；
- Runner 勾选 `Keep variable values` 后，将运行期间更新的变量保留在 Collection 中。

清除认证 Session 后直接请求 Employee Search，服务器的实际响应为：

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "error": {
    "status": 401,
    "message": "Session expired"
  }
}
```

响应同时可能设置新的匿名 Session Cookie，但匿名 Cookie 不等于已经登录。

### 我的理解

- Cookie 保存的是客户端与服务器之间的 Session 标识，浏览器登录成功不代表 Postman 自动登录；
- CSRF Token 和生成它的 Session Cookie 需要成对使用；
- 查询条件 `employeeId` 只能说明“查谁”，认证 Cookie 才能说明“我是谁、是否有权查询”；
- 自动化断言不能只验证状态码，还要验证重定向目标、响应格式和关键业务字段；
- 公共 Demo 的数据会变化，固定 Employee ID 不适合作为长期测试数据；先创建数据、保存返回值、再查询验证更稳定；
- Collection 中前置请求准备认证和测试数据，后续请求消费变量，这就是最基础的接口工作流和数据依赖。

---

# 2026-09-07

## 4. Requests CRUD 中的真实响应差异

### 遇到的问题

将 Postman 流程改写为 Requests 脚本时，CRUD 链路出现过两个实际失败：

- Employee Search 携带 `includeEmployees=currentOnly` 后返回 `422 Invalid Parameter`；
- Delete 接口返回的员工编号是字符串，而 Create 响应中的 `empNumber` 是整数，直接比较会断言失败。

### 原因

接口参数和响应字段类型应以当前 OrangeHRM 的真实响应为准，不能仅凭名称推测，也不能假设不同接口会用相同 JSON 类型返回同一个业务标识。

### 排查过程

1. 打印并检查失败响应的状态码与 JSON，确认 422 指向 `includeEmployees`；
2. 对比 Create 和 Delete 响应，确认员工编号分别为整数和字符串；
3. 每次调整后重新运行完整链路，验证创建、查询、修改、删除及删除后查询。

### 解决方式

- Search 只保留已验证有效且本场景必需的 `employeeId` 参数；
- 比较删除结果前，将 `empNumber` 转换为字符串；
- 一条龙脚本保留 `finally` 清理，避免中途断言失败时遗留公共 Demo 数据。

### 我的理解

- 自动化测试应观察真实请求和响应，不应把 Postman 中的旧参数机械迁移到代码；
- JSON 中的 `274` 和 `"274"` 业务含义可能相同，但 Python 类型不同，断言时需要明确处理；
- 清理逻辑不是只为“全部通过”设计的，更重要的是在测试失败时恢复环境。

---

## 5. 从一条龙 Requests 脚本拆分为 API 请求层和 Pytest 测试层

### 遇到的问题

一条龙脚本能够证明完整业务链可运行，但登录、数据准备、业务操作、断言和清理集中在同一个流程中。任一步骤失败都会阻断后续验证，也难以从测试名称直接定位失败场景。

### 原因

脚本适合初次理解接口依赖链；进入重复回归后，需要把“如何发请求”和“验证什么业务行为”分开，并让每条员工测试拥有独立的数据生命周期。

### 解决方式

- `auth_api.py` 中的 `login` 函数和 `EmployeeAPI` 只负责组装并发送 HTTP 请求，返回原始 `Response`；
- 测试文件负责状态码、JSON 字段和业务状态变化断言；
- `login_context` 使用 session scope，在整次测试会话中复用一个已登录的 `requests.Session`，减少重复登录，同时保持 Cookie 状态；
- `employee_api` 使用 session scope，共享只包含请求方法的 API Client；
- `created_employee` 使用 function scope，每条员工测试单独创建动态 Employee ID，并通过 `yield` 在测试结束后执行 teardown；
- 账号和密码从环境变量读取，不写入源码；缺少凭证时跳过依赖登录的测试。

### 为什么这样选择 scope

登录状态和 API Client 在本轮测试中可安全复用，因此使用 session scope；测试员工会被修改或删除，属于可变业务数据，因此使用 function scope，防止不同测试相互污染。

### cleanup 的容错

teardown 删除测试员工时接受 `200` 或 `404`：`200` 表示清理成功；`404` 表示员工已经被测试步骤删除或当前已不存在，也达到了“环境中不残留该数据”的清理目标。这种容错只用于清理阶段，不会放宽业务测试本身的断言。

### 后续修正：AAA 职责边界

- Arrange 负责准备前置条件和输入数据；
- Act 负责执行当前用例真正要验证的业务动作；
- Assert 负责验证 HTTP 结果和关键业务结果。

`test_create_employee` 最初把 Create 动作放在 `created_employee` fixture 中，导致测试主体看不到真正的 Act。后续将 `employee_data` 调整为只生成请求数据，由测试函数显式执行 Create；`created_employee` 中的 Create 则只服务于 Search / Update / Delete，因为对这些测试来说，预先存在的员工属于 Arrange。fixture 可以复用公共前置，但不应因此隐藏当前用例真正需要验证的 Act。

### 验证结果

执行命令：

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests\api -v -p no:cacheprovider
```

实际结果：`6 passed`。覆盖登录成功、未认证访问返回 401，以及员工创建、查询、修改后查询、删除后查询。

### 我的理解

- fixture 用于管理多个测试共享的前置条件或资源生命周期，不是为了隐藏所有业务步骤；
- `yield` 之前是 setup，之后是 teardown；即使测试断言失败，Pytest 仍会进入 fixture 的清理部分；
- API 请求层回答“怎样调用接口”，测试层回答“这个行为是否符合预期”；
- 环境变量把凭证和运行配置留在执行环境中，既避免敏感信息进入 Git，也允许同一套测试切换环境；
- 拆分后的六条测试可以独立报告失败，比把原流程塞进一个测试函数更容易定位和解释。

---

## 6. Pytest 参数化与 Marker 分类

### parametrize

- `pytest.mark.parametrize` 适合同一套测试步骤和断言需要覆盖多组输入的场景，避免复制多个结构相同的测试函数；
- Pytest 会在 collection 阶段把参数化数据展开为独立 case，因此每组数据会单独执行、单独显示结果；
- `pytest.param(..., id="...")` 可以为 case 提供有业务含义的名称，比默认参数值更便于阅读报告和定位失败；
- 本轮在确认 OrangeHRM Demo 对空 `firstName` 和空 `lastName` 均真实返回 `422 Invalid Parameter` 后，才将两组必填字段校验写成参数化断言。

### marker

- `smoke` 用于快速确认登录、创建、查询等核心能力是否基本可用；
- `regression` 用于执行更完整的回归集合，包括异常场景和员工 CRUD；
- 一条核心用例可以同时属于 `smoke` 和 `regression`，因为它既承担快速检查，也属于完整回归范围；
- `pytest -m` 用于按 marker 表达式筛选测试，不是执行 Pytest 时必须提供的参数。

---

# 2026-09-08

## 7. 测试数据管理与 DDT

### DDT 是测试设计思想

DDT（Data-Driven Testing，数据驱动测试）的核心是让同一套测试步骤和断言消费多组数据，而不是为每组输入复制一份测试代码。JSON、YAML 只是可选的数据来源格式，并不等于 DDT 本身；本阶段使用 JSON 已经完成了外部数据驱动实践，因此没有重复引入 YAML。

### 不同数据应按生命周期分开管理

- 环境变量保存运行地址和环境凭证；
- Factory 生成每次运行需要的动态合法业务输入；
- JSON 保存固定且已经确认的测试 case 与 expected；
- API Response 和 fixture context 保存 `empNumber` 等运行时结果。

这种划分不是把所有数据机械搬到文件里，而是让敏感配置、动态输入、固定规则和运行结果各自归位。

### Faker、Factory 与 overrides 的职责

Faker 只提供模拟姓名原料；Factory 负责把姓名、动态 Employee ID 和其他必需字段组合成完整合法 payload。先生成合法基础数据，再通过 overrides 只修改当前场景关注的字段，可以减少重复字典，也能清楚看出异常 case 与正常数据的差异。

函数定义中的 `**overrides` 会把调用方传入的关键字参数收集成一个 dict。`dict.update` 遇到已有 key 时更新原值，遇到不存在的 key 时会新增；因此 overrides 既灵活，也要求调用方使用正确字段名。

### 降低 flaky 的防御性处理

- `Path(__file__)` 从数据模块自身位置定位 JSON，避免依赖绝对路径或执行命令时的当前目录；
- Faker 姓名经过 ASCII 字母清洗，避免随机特殊字符触发公共 Demo 的非预期校验；
- 时间戳 Employee ID 增加当前进程内去重，处理系统时钟精度不足造成的快速重复；
- cleanup 接受 `200` 或 `404`，因为二者都表示临时员工最终不存在，但这种容错只用于清理阶段，不会放宽业务断言。

这些处理不是为了掩盖失败，而是为了减少与测试目标无关的随机干扰，让真正的业务失败更容易定位。

---

## 8. Docker 本地测试环境与持久化

### 为什么是两个服务、两个 volume

Phase 6 收口时，Compose 只管理 OrangeHRM 和 MariaDB 两个服务。OrangeHRM 通过服务名 `db` 和容器端口 `3306` 连接数据库；当时宿主机只把 `8080` 映射到 Web 容器的 `80`，尚未发布数据库端口。

MariaDB 数据放在 `orangehrm_quality_lab_db_data`，因为容器重建不应删除业务数据。OrangeHRM 官方 image 还声明了 `/var/www/html` volume，安装器生成的连接配置也在该目录中，因此使用第二个显式 named volume `orangehrm_quality_lab_app_data`。否则 Docker 会创建匿名 volume，down 后再次 up 不会自动复用原来的安装状态。

这说明“数据库有 volume”不一定就足够：还要检查应用把环境特有配置写在哪里。当前方案的代价是应用 volume 会遮蔽以后新 image 中的文件，因此未来升级版本需要单独迁移，不能只改 tag。

### 实际问题一：Docker 已安装，但旧进程的 PATH 未刷新

Docker Desktop 以当前用户安装到 `AppData\Local\Programs\DockerDesktop` 后，当前 Codex PowerShell 仍报告找不到 `docker`。从卸载注册表和安装目录确认软件已存在，并直接调用 `resources\bin\docker.exe` 后，Client、Server 和 Compose 都能正常返回版本。

第一次只调用绝对路径拉取 image 时又出现 `docker-credential-desktop` 找不到。原因是 Docker CLI 能启动，但 credential helper 所在目录仍不在当前进程 PATH。临时把完整 `resources\bin` 加到该进程 PATH 后拉取成功。正常使用时重新打开终端或 Codex，让安装后的 PATH 生效即可。

### 实际问题二：已弃用的 CLI “帮助”参数仍触发安装

执行旧入口 `php installer/cli_install.php --help` 时，它先提示该入口已弃用，却继续读取镜像自带示例配置并尝试连接 `127.0.0.1`，最终返回 `Connection refused`。

容器中的 `127.0.0.1` 只指向 OrangeHRM 容器自己，不是 MariaDB 容器。检查确认没有生成安装配置，MariaDB 也未受影响。随后改用提示中的新版命令：

```powershell
docker compose exec orangehrm sh -lc "cd /var/www/html && php installer/console install:on-existing-database"
```

数据库 Host 填 Compose 服务名 `db`。安装器的系统检查实际识别到 MariaDB `10.11.19`，数据库迁移、管理员创建和配置生成全部完成。

### 实际验收与理解

- `depends_on` 配合 MariaDB healthcheck，使 OrangeHRM 等待数据库真正可连接，而不只是等待 DB 容器进程被创建；
- 首次启动 HTTP `200` 页面位于 `/installer/index.php/welcome`，安装完成后变为 `/web/index.php/auth/login`；
- MariaDB 日志中的 `io_uring` 回退和 Apache 的 `ServerName` 提示是非阻塞警告，healthcheck、数据库 ping、HTTP 和 smoke 均通过；
- 不带 `-v` 执行 down/up 后，两个 volume 的创建时间不变，MariaDB 日志显示无需重新初始化，OrangeHRM 仍进入登录页；
- 重启前后本地 smoke 均为 `3 passed`，说明登录、员工创建和查询在本地环境真实可用；
- Phase 6 收口时只确认数据库服务和应用连接，没有查询业务表，也没有编写数据库断言；这些内容后来在 Phase 7 完成。

---

# 2026-09-09

## 9. API 响应与数据库最终状态校验

### 为什么引入 PyMySQL

Python 标准库没有 MySQL / MariaDB 驱动。本阶段选择 PyMySQL，是因为它可以直接从宿主机建立连接、参数化执行 SQL，并用 `DictCursor` 返回按列名读取的结果。也可以在测试外调用 MariaDB CLI 完成一次性查询，但不便集成到 Pytest 断言；本阶段只有简单 `SELECT`，因此没有引入 SQLAlchemy 或 ORM。

`utils/db.py` 只保留创建连接和 `fetch_one`。cursor 在查询函数的 `with` 中关闭，connection 由 function-scope fixture 在 `yield` 后关闭。数据库名、用户和密码必须来自环境变量，Host / Port 为本地环境提供 `127.0.0.1 / 3307` 默认值。

### 容器连接与宿主机连接是两条链

```text
OrangeHRM Container → db:3306
Windows Pytest      → 127.0.0.1:3307 → MariaDB Container:3306
```

Compose 中增加的数据库端口只绑定 `127.0.0.1`，不会把 MariaDB 发布到所有网卡；OrangeHRM 自身仍使用服务名 `db` 和容器端口 `3306`。`ORANGEHRM_DB_HOST_PORT` 用于 Compose 端口映射，`ORANGEHRM_DB_PORT` 用于 PyMySQL 连接，两者默认都是 `3307`，但不是同一个进程中的配置。

Compose 会读取 `.env` 做变量替换，却不会把变量导出到启动 pytest 的 PowerShell。因此运行 DB tests 前仍需在同一个 PowerShell 中显式设置 API 与数据库环境变量；测试代码不会主动读取 `.env`，也没有为此增加 `python-dotenv`。

### 先核验真实 schema，再写断言

在当前 OrangeHRM 5.9 / MariaDB 10.11.19 中实际确认表 `hs_hr_employee` 存在，相关列为：

- `emp_number int(11) NOT NULL PRIMARY KEY`；
- `employee_id varchar(50) NULL`；
- `emp_firstname varchar(100) NOT NULL`；
- `emp_middle_name varchar(100) NOT NULL`；
- `emp_lastname varchar(100) NOT NULL`。

自动化查询只用参数化条件 `WHERE emp_number = %s` 定位唯一员工，再由 Python 分别断言 Employee ID 和姓名字段。没有把所有期望值都塞进 `WHERE`，否则查询不到记录时无法分辨是记录不存在，还是某一个字段不一致。

Create / Update / Delete 都先严格验证 API 响应，再执行数据库 `SELECT`：创建后断言行存在且字段一致，修改后断言同一主键的姓名已更新，删除后断言查询返回 `None`。这里的 `SELECT` 就是 Assert；测试数据的业务操作和 cleanup 仍通过现有 `EmployeeAPI`，没有用 SQL `DELETE` 绕过系统行为。

### SQL 基础练习的实际结果

本轮只把业务真正需要的 `SELECT / WHERE` 放入自动化测试。其余语法在同一数据库执行了只读练习：

- `SELECT COUNT(*) FROM hs_hr_employee` 返回 `1`；
- `SELECT emp_number FROM hs_hr_employee ORDER BY emp_number DESC LIMIT 3` 返回当时唯一的 `emp_number=1`；
- `hs_hr_employee INNER JOIN ohrm_user ON ohrm_user.emp_number = hs_hr_employee.emp_number` 的关联数量为 `1`；外键元数据也确认了这组关联键。

COUNT 用于聚合记录数量，ORDER BY 用于明确结果顺序，JOIN 用于按已确认的关联键组合两张表。本阶段只验证基本使用，不扩展索引、事务隔离、锁或执行计划。

### 实际问题：删除响应中的 ID 类型因环境不同

官方公共 Demo 之前返回字符串 ID，例如 `['274']`；本地 OrangeHRM 5.9 本轮实际返回整数 ID，例如 `[8]`。原断言只接受字符串，导致首次 DB tests 结果为 `2 passed, 1 failed`，但删除动作本身已经成功，teardown 再次删除得到可接受的 `404`，没有留下测试数据。

最终断言先严格确认响应列表只有一个元素和值类型只能是 `int` 或 `str`，再要求它精确等于 `emp_number` 或对应字符串。这样只兼容已经实际观察到的 JSON 表示差异，不会用宽泛类型转换误接受浮点数等其他值，也不会放宽删除数量或员工身份的判断。修正后 DB tests 为 `3 passed`，完整 API tests 为 `8 passed`，smoke 为 `3 passed, 9 deselected`，本地完整测试集合为 `12 passed`。

---


