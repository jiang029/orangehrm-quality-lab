# OrangeHRM Quality Lab

基于 OrangeHRM 开源人力资源管理系统构建的测试开发学习与求职展示项目。

本项目不追求覆盖 OrangeHRM 的全部功能，而是选择少量核心业务链，逐步完成业务分析、接口测试、接口自动化、数据库校验、UI 自动化和持续集成。每个阶段既要求实践结果能够运行，也要求能够解释设计原因、排查过程和替代方案。

## 测试范围

核心业务：

- Login：登录、退出、基础鉴权与权限场景；
- PIM：Add Employee、Employee Search、Edit Employee；
- Leave：Apply Leave、管理员审批、员工查看状态。

辅助范围：

- Admin：仅关注 System Users、员工与登录账号关联、Admin / ESS 角色；
- My Info：仅验证当前用户资料及其与 PIM 的权限和数据一致性；
- Dashboard：只作为登录成功后的落地页。

项目不扩展其他 OrangeHRM 模块，目标是形成“小而完整、能够在面试中讲透”的测试项目。

## 当前进度

- [x] Phase 0：项目初始化
- [x] Phase 1：业务分析与手工测试设计
- [x] Phase 2：HTTP 与 Postman 接口测试
- [x] Phase 3：Python Requests 接口自动化
- [x] Phase 4：Pytest 工程化
- [x] Phase 5：测试数据管理
- [x] Phase 6：Docker 本地测试环境
- [x] Phase 7：MySQL 数据库校验
- [x] Phase 8：Playwright UI 自动化
- [ ] 后续阶段：测试报告与 CI

详细计划和状态见 [docs/ROADMAP.md](docs/ROADMAP.md)。

## Phase 2 实践成果

通过浏览器 DevTools 确认 OrangeHRM 当前版本的真实请求结构，并在 Postman 中完成以下依赖链：

```text
GET Login Page
      ↓ 获取 Session Cookie 和 CSRF Token
POST Login
      ↓ 建立已认证 Session
POST Add Employee
      ↓ 保存动态生成的 employeeId
GET Search Employee
      ↓ 验证创建与查询数据一致
```

已完成：

- 使用 Cookie Jar 自动维护 Session Cookie；
- 从登录页动态提取 CSRF Token，并通过 Collection Variable 传递；
- 使用动态 Employee ID 准备可控测试数据，避免依赖公共 Demo 的固定员工；
- 使用 Collection Runner 顺序执行 4 个请求，8 个断言全部通过；
- 清除认证 Session 后直接查询员工，确认服务器返回 `401 Unauthorized` 和 `Session expired`。

Postman 中只保存请求结构和非敏感测试逻辑，不应提交账号密码、Cookie、Token 等认证信息。

## Phase 8 实践成果

使用 Python Playwright 与 Pytest 在本地 Docker OrangeHRM 上完成 5 条关键 UI smoke：

- 有效管理员登录进入 Dashboard；
- 错误密码登录显示明确反馈；
- 通过 UI 创建动态员工，并在个人详情页校验姓名和 Employee ID；
- API 创建员工后，通过 UI 按动态 Employee ID 查询唯一结果；
- 查询不存在的动态 Employee ID，校验空结果和空数据表。

Locator 以 role、placeholder 和动态业务文本为主，依靠 Playwright actionability 与 web-first assertion 自动等待，没有使用固定 sleep、XPath 或全局索引。最小链路跑通并出现重复后，只提取了 `LoginPage` 和 `EmployeePage`；测试数据继续复用现有 Factory / Employee API 做前置与清理。

Pytest 默认只在失败时保留全页 Screenshot 和 Trace，产物位于已被 Git 忽略的 `test-results/`。Trace 可能包含页面输入、Cookie 和网络信息，只用于本地排查，不能提交或公开。本轮最终使用本机 Chrome channel 连续运行两轮，均为 `5 passed`，未发现 flaky；原有 API + DB 关键回归为 `11 passed`，本地完整集合为 `17 passed`。

Leave 状态流转需要独立 ESS 账号、假期类型、额度和 Admin 审批等额外前置，本阶段没有为凑用例数量强行加入。

## 当前技术栈

已经实践：

- Python 3.12
- Pytest
- Postman
- Git / GitHub
- 浏览器 DevTools
- Requests
- Faker
- JSON 数据驱动测试
- Docker Desktop / Docker Engine
- Docker Compose
- MariaDB 10.11 本地测试环境
- PyMySQL
- API 响应与 MariaDB 最终状态联合断言
- Python Playwright / pytest-playwright
- Chrome channel UI 自动化
- Locator、自动等待、失败 Screenshot / Trace
- 简单 Page Object

后续按路线逐步引入：

- Allure
- GitHub Actions

## 项目文档

- [业务范围与规则](docs/business_notes.md)
- [测试点](docs/test_points.md)
- [学习路线](docs/ROADMAP.md)
- [学习记录](docs/LEARNING_LOG.md)
- [Docker 本地环境](docs/DOCKER_SETUP.md)
- [项目协作规则](AGENTS.md)

## 项目原则

- 优先覆盖稳定、核心、高频回归场景；
- 已知业务规则与待验证假设明确区分；
- 测试点关注风险覆盖，不追求数量；
- 测试数据尽量可控，不依赖公共环境中的固定记录；
- AI 输出仅作为分析建议，最终结论必须经过实际验证；
- 只记录和展示已经真实完成、能够解释的技术实践。
