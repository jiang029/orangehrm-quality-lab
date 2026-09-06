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
- [ ] Phase 3：Python Requests 接口自动化（当前阶段）
- [ ] 后续阶段：Pytest 工程化、测试数据管理、Docker、数据库、UI 自动化、测试报告与 CI

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

## 当前技术栈

已经实践：

- Python 3.12
- Pytest
- Postman
- Git / GitHub
- 浏览器 DevTools

后续按路线逐步引入：

- Requests
- MySQL / MariaDB、PyMySQL
- Docker / Docker Compose
- Playwright
- Allure
- GitHub Actions

## 项目文档

- [业务范围与规则](docs/business_notes.md)
- [测试点](docs/test_points.md)
- [学习路线](docs/ROADMAP.md)
- [学习记录](docs/LEARNING_LOG.md)
- [项目协作规则](AGENTS.md)

## 项目原则

- 优先覆盖稳定、核心、高频回归场景；
- 已知业务规则与待验证假设明确区分；
- 测试点关注风险覆盖，不追求数量；
- 测试数据尽量可控，不依赖公共环境中的固定记录；
- AI 输出仅作为分析建议，最终结论必须经过实际验证；
- 只记录和展示已经真实完成、能够解释的技术实践。
