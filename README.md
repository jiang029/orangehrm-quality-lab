# OrangeHRM Quality Lab

基于 OrangeHRM 5.9 的测试开发实践项目。项目使用少量、可重复的 Login 与 PIM 核心场景，串联 API 自动化、MariaDB 持久化断言、Playwright UI smoke、Allure 诊断、Git Pull Request、GitHub Actions CI 和 AI 辅助代码变更影响分析。

本项目不追求完整覆盖 OrangeHRM，也不把它包装成“企业级框架”。重点是让每项成果都经过真实执行，并能够解释测试范围、设计取舍和已知限制。

## 项目状态

| 项目事实 | 当前状态 |
|---|---|
| 被测系统 | OrangeHRM `5.9` + MariaDB `10.11.19` |
| 已自动化范围 | Login、PIM Employee 核心场景 |
| 本地完整测试 | `17 passed`：API 8 + DB 3 + UI 5 + 环境检查 1 |
| Git 协作 | feature branch → PR #1 → merge → main |
| 远端 CI | PR 与 main push 两次 GitHub Actions 均成功 |
| Allure | 本地可生成 HTML；CI 仅保存 3 天原始 results artifact |
| AI 辅助实践 | 已完成一次基于真实历史 diff 的变更影响分析与回归验证 |

项目阶段以 [ROADMAP](docs/ROADMAP.md) 为唯一事实来源。

## 测试链

```text
OrangeHRM 5.9
      ↓
Requests API automation
      ↓
MariaDB persistence assertion
      ↓
Playwright UI smoke
      ↓
Allure failure diagnostics
      ↓
Git branch / Pull Request
      ↓
GitHub Actions CI
      ↓
AI-assisted change impact analysis
```

接口层承担主要业务回归，数据库层只校验关键最终状态，UI 层只保留用户真正依赖的 smoke 链路。这样能减少脆弱且重复的 UI 用例，同时保留从请求、落库到页面的分层证据。

## 被测范围与测试策略

### 已实现的自动化

| 层 | 数量 | 主要场景 | 作用 |
|---|---:|---|---|
| API | 8 | 登录成功、未认证查询 401、Employee Create / Search / Update / Delete、姓名必填校验 | 快速覆盖核心业务与异常行为 |
| Database | 3 | Employee 创建、修改、删除后的 MariaDB 最终状态 | 防止只相信 API 成功响应 |
| UI | 5 | 有效/无效登录、UI 创建员工、查询已有/不存在员工 | 验证少量关键用户链路 |
| Environment | 1 | Python 测试环境基础自检 | 尽早暴露执行环境问题 |

自动化用例创建的临时员工数据均动态生成，并在测试后通过业务 API 清理。数据库测试只执行参数化 `SELECT` 作为断言，不使用 SQL 绕过系统创建、修改或删除数据。

### 明确未实现的范围

- Leave 已完成业务梳理和测试点设计，但没有自动化。完整流程需要 ESS 账号、员工关联、假期类型、额度、有效日期和审批状态等独立前置。
- Admin 与 My Info 仅用于理解角色、账号关联和数据边界，没有对应自动化用例。
- 没有声称覆盖 OrangeHRM 全部模块、全部权限或全部浏览器组合。

相关手工分析见 [业务说明](docs/business_notes.md) 与 [测试点](docs/test_points.md)。

## 核心实现

### API 自动化与测试数据

- 先用浏览器 DevTools 与 Postman 确认真实 URL、Method、Session Cookie、CSRF Token 和响应结构，再将已验证链路实现为 Requests 自动化。
- `requests.Session` 复用登录页 Cookie，并从 HTML 动态提取 CSRF Token；登录提交保留原始 `302 Location` 作为断言依据。
- `EmployeeAPI` 只负责请求组装并返回原始 Response，业务断言留在测试层。
- session-scope fixture 复用认证会话与 API Client；function-scope fixture 隔离每条可变员工数据，并用 `yield` 管理 teardown。
- Factory + Faker 生成 ASCII 姓名和进程内不重复的 10 位 Employee ID；`**overrides` 复用合法 payload 构造异常输入。
- 已确认的必填字段 case 保存在 JSON 中，由 `pytest.mark.parametrize` 展开为独立结果。

### Docker 与 MariaDB 持久化校验

Docker Compose 管理 OrangeHRM 与 MariaDB。OrangeHRM 容器通过 `db:3306` 访问数据库；宿主机 PyMySQL 通过 `127.0.0.1:3307` 查询同一实例。两个 named volumes 分别保存数据库数据和 OrangeHRM 安装状态，普通 `down/up` 后仍可恢复。

数据库测试用 API 创建或修改 Employee，再按 `emp_number` 查询 `hs_hr_employee`，分别核对 Employee ID 与姓名字段；Delete 后确认记录不存在。详细环境说明见 [Docker 本地环境](docs/DOCKER_SETUP.md)。

### Playwright UI smoke

UI 用例使用 role、placeholder 和动态业务文本定位，依靠 Playwright actionability 与 web-first assertion 自动等待，没有固定 sleep、XPath 或全局 `nth()` 定位。仅在重复行为真实出现后提取 `LoginPage` 和 `EmployeePage`，没有增加 BasePage 或多层通用封装。

pytest-playwright 只在失败时保留全页 Screenshot 与 Trace。Trace 可能包含页面输入、Cookie、DOM 和网络数据，因此 `test-results/` 被 Git 忽略，只用于受控排查。

### Allure 诊断

`allure-pytest` 将 Pytest 状态、业务标签、关键步骤与附件写入 `allure-results/`。API Response、数据库实际行以及 UI 失败时的 Screenshot / Trace 可作为诊断上下文；本机 Allure CLI 可将原始结果渲染为 `allure-report/`。

CI 上传的是可重新渲染的原始 `allure-results`，保留 3 天。项目没有部署 GitHub Pages，也没有长期在线报告站点或历史趋势服务。

### Git branch、Pull Request 与 GitHub Actions

Phase 10/11 使用真实变更完成了 `feat/github-actions-ci` → [Pull Request #1](https://github.com/jiang029/orangehrm-quality-lab/pull/1) → merge → main push 的协作链：

- [PR CI run](https://github.com/jiang029/orangehrm-quality-lab/actions/runs/34563046220)：成功；
- [main push CI run](https://github.com/jiang029/orangehrm-quality-lab/actions/runs/34563486889)：成功。

workflow 在 `ubuntu-24.04` 上从空数据库启动 OrangeHRM 与 MariaDB，安装 Python 依赖和 Playwright Chromium，单次执行完整 17 条测试，并通过 JUnit 与 Allure 原始结果交叉检查测试数、`skipped=0` 和全部 passed。两次 run 均成功上传短期 `allure-results` artifact，并完成 runner 内 Docker 资源清理。

### AI 辅助代码变更影响分析

Phase 12 选择历史 commit `9614e02` 作为真实输入：四个 fixture 从 `tests/api/conftest.py` 原样移动到 `tests/conftest.py`。虽然 diff 是 100% rename、没有实现行变化，但 Pytest 的目录发现规则改变了 fixture 可见范围。对该提交当时的测试树而言，新增行为是 DB 子树获得 fixture；API 子树仍可使用它们，UI 当时尚不存在。

分析随后以当前 HEAD 回答“今天再次修改这组共享 fixture，应回归谁”：通过 `git diff --find-renames`、`rg`、fixture 参数和依赖链识别 13 条现有消费者。依据引用证据和项目测试策略复核后，本次采用这 13 条消费者回归集，在本地 OrangeHRM + MariaDB + Chrome 环境执行为 `13 passed`；这不是历史 commit 的前后对照证明。最终业务范围仍需测试人员确认。完整过程见 [Learning Log](docs/LEARNING_LOG.md)，可复用指南见 [change-impact-analysis skill](skills/change-impact-analysis/SKILL.md)。

AI 在这里负责检索、依赖分析、风险提示和回归建议；最终范围、业务判断、实际执行和 Bug 结论仍由测试人员确认。

## 技术栈

| 类别 | 技术 |
|---|---|
| Language / Test | Python 3.12、Pytest |
| API | Browser DevTools、Postman、Requests |
| Test data | Faker、JSON、Pytest parametrize、Factory |
| Environment | Docker Desktop、Docker Compose、OrangeHRM 5.9 |
| Database | MariaDB 10.11、PyMySQL、参数化 SQL |
| UI | Playwright、pytest-playwright、Page Object |
| Diagnostics | Allure Pytest、Allure CLI、Screenshot、Trace、JUnit XML |
| Collaboration / CI | Git、GitHub Pull Request、GitHub Actions |
| AI-assisted testing | Git diff、引用搜索、影响分层、人工确认的回归范围 |

## 项目目录

```text
.github/workflows/test.yml       # PR / main push 集成测试
api/                             # 登录与 Employee API 请求层
pages/                           # Login / Employee Page Object
tests/
├── api/                         # 8 条 API 测试
├── db/                          # 3 条 MariaDB 持久化测试
├── ui/                          # 5 条 Playwright UI smoke
├── data/                        # Factory 与 JSON case
├── conftest.py                  # 跨层共享 fixture
└── test_environment.py          # 环境自检
utils/db.py                      # 最小数据库连接与查询层
skills/change-impact-analysis/   # 可复用影响分析指南
docs/                            # 业务、测试点、路线与学习记录
docker-compose.yml               # OrangeHRM + MariaDB
pytest.ini                       # markers 与失败产物配置
requirements.txt                 # Python 直接依赖
```

## 本地运行

### 1. 安装 Python 依赖

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

本地 UI 验收使用系统 Chrome；CI 使用 Playwright bundled Chromium。`.venv/` 不属于项目源码，不应提交。

### 2. 启动本地 OrangeHRM

```powershell
Copy-Item .env.example .env
# 将 .env 中的 password placeholder 替换为仅供本地使用的值
docker compose config --quiet
docker compose up -d
docker compose ps
```

首次启动还需完成 OrangeHRM 初始化；请按 [Docker 本地环境](docs/DOCKER_SETUP.md#启动与初始化) 使用当前 5.9 对应步骤。`.env` 已被 Git 忽略，不能提交。

### 3. 把本地配置导出给 Pytest

Compose 会读取 `.env` 做变量替换，但不会把变量导出到当前 PowerShell。可在同一个终端中加载本项目的简单 `KEY=VALUE` 配置：

```powershell
Get-Content .env |
    Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } |
    ForEach-Object {
        $name, $value = $_ -split '=', 2
        Set-Item -Path "Env:$name" -Value $value
    }
```

### 4. 执行完整测试

```powershell
.\.venv\Scripts\python.exe -B -m pytest -v -p no:cacheprovider `
    --strict-markers --browser-channel chrome --junitxml=pytest-results.xml
```

在本地服务、数据库、凭证和 Chrome 均就绪时，应收集 17 条测试且不应出现 skip。DB / UI fixture 会在缺少本地环境变量时 skip；因此不能把有 skip 的绿色结果当作完整验收。

### 5. 生成本地 Allure HTML

```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
```

Allure CLI 与 Java 是独立系统工具，不在 `requirements.txt` 中；Python 依赖只负责生成原始 results。`allure-results/`、`allure-report/`、`test-results/` 和 `pytest-results.xml` 均为被忽略的运行产物。

## 已知限制与权衡

- 自动化集中在 Login 与 PIM Employee；Leave、Admin、My Info 未自动化。
- UI 只保留 5 条 smoke，没有把所有 API 回归重复成浏览器操作。
- CI 固定 OrangeHRM `5.9`，但首次初始化依赖镜像中已 deprecated 的 YAML 兼容入口；升级 image 必须重新验证。
- Compose image 使用版本 tag 而非 digest，Python 只固定直接依赖；复现性尚未达到镜像 digest + 全量 hash lock。
- CI 依赖 Docker Hub、PyPI 与 Playwright CDN，外部下载故障仍可能造成环境失败。
- Allure CI artifact 只保留 3 天原始结果，没有在线站点、长期历史或趋势图。
- 静态影响分析可能遗漏动态调用、运行时配置和业务语义，不能替代真实回归与人工结论。

## 文档入口

- [项目路线与阶段状态](docs/ROADMAP.md)
- [真实问题与实践记录](docs/LEARNING_LOG.md)
- [Docker 本地环境](docs/DOCKER_SETUP.md)
- [业务范围与规则](docs/business_notes.md)
- [测试点](docs/test_points.md)
- [项目协作规则](AGENTS.md)
- [影响分析操作指南](skills/change-impact-analysis/SKILL.md)
