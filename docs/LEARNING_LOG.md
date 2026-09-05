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
```