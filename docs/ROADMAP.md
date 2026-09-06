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
| Phase 3 | Requests 接口自动化 | 🚧 进行中 |
| Phase 4 | Pytest 工程化 | ⬜ 未开始 |
| Phase 5 | 测试数据管理 | ⬜ 未开始 |
| Phase 6 | Docker 本地测试环境 | ⬜ 未开始 |
| Phase 7 | MySQL 数据库校验 | ⬜ 未开始 |
| Phase 8 | Playwright UI 自动化 | ⬜ 未开始 |
| Phase 9 | Allure 测试报告 | ⬜ 未开始 |
| Phase 10 | Git 分支与 Pull Request | ⬜ 未开始 |
| Phase 11 | GitHub Actions 持续集成 | ⬜ 未开始 |
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

# Phase 3｜Python Requests 接口自动化 🚧
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

- [ ] 使用 Requests 编写第一个 GET 请求
- [ ] 理解 Response、status_code、text 和 json()
- [ ] 编写基础接口断言
- [ ] 使用 requests.Session 跑通 OrangeHRM 登录
- [ ] 使用 Python 完成员工创建和查询
- [ ] 完成员工修改和删除，形成基础 CRUD 链路
- [ ] 补充少量有价值的异常场景
- [ ] 在出现明显重复代码后，再进行 Employee API Client 基础封装
---

# Phase 4｜Pytest 工程化
## 目标

使用 Pytest 管理测试前置、测试数据和测试分类。

## 学习内容
- fixture
- conftest.py
- fixture scope
- parametrize
- marker
- setup / teardown

## 重点问题
需要能够解释：
- 为什么要使用 fixture？
- 为什么登录 Token 可以使用 session scope？
- 为什么测试数据适合使用参数化？

---

# Phase 5｜测试数据管理
## 目标

避免自动化测试大量使用写死的数据。

## 计划引入
- Faker
- 时间戳
- YAML / JSON
- 测试数据工厂

## 实践内容
例如自动生成：`QA_User_20260905_xxxx`

避免：
- Tom
- Tom2
- test123

## 重点理解
测试数据与测试逻辑分离。

---

# Phase 6｜Docker 本地部署 OrangeHRM
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

## 常用命令
- docker ps
- docker compose up -d
- docker compose down
- docker logs

## 验收标准
能够解释：为什么项目需要 Docker，而不是只说“我会 Docker”。

---

# Phase 7｜MySQL 数据库校验
## 目标

在接口响应校验之外，进一步验证数据库最终状态。

## 示例
```text
POST 创建员工
      ↓
接口返回 employee_id
      ↓
查询数据库
      ↓
确认员工记录真实存在
```

## 学习内容
- SELECT
- WHERE
- ORDER BY
- COUNT
- JOIN
- PyMySQL

## 计划目录
```text
utils/
└── db.py
```

## 重点理解
接口响应断言 + 数据库状态断言

---

# Phase 8｜Playwright UI 自动化
## 目标

对少量关键业务流程进行 Web UI 冒烟自动化。

## 主要场景
- 登录
- 创建员工
- 查询员工
- 请假核心流程

## 学习内容
- Locator
- 自动等待
- Screenshot
- Trace
- Page Object

## 计划目录
```text
pages/

tests/
└── ui/
```

## 自动化原则
接口自动化负责主要业务验证，UI 自动化只覆盖核心用户链路。

---

# Phase 9｜Allure 测试报告
## 目标

提高测试执行结果和失败信息的可读性。

## 学习内容
- allure-results
- allure generate
- allure serve
- feature
- story
- severity
- step
- attachment

## 重点
Allure 的价值不是单纯“报告漂亮”，而是帮助定位：
- 哪条用例失败；
- 哪一步失败；
- 实际结果是什么。

---

# Phase 10｜Git 分支与 Pull Request
## 目标

模拟实际团队 Git 协作流程。

## 计划练习
```text
main
 ├── feat/api-tests
 └── feat/ui-tests
```

## 学习内容
- 创建分支
- 切换分支
- commit
- push
- Pull Request
- merge

---

# Phase 11｜GitHub Actions CI
## 目标

实现代码提交后自动执行测试。

## 流程
```text
Push / Pull Request
        ↓
GitHub Actions
        ↓
Checkout Code
        ↓
安装 Python
        ↓
安装 requirements
        ↓
pytest
        ↓
生成测试结果
```

## 计划文件
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
