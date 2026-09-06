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


