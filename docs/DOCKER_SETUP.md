# OrangeHRM 本地 Docker 环境

## 为什么引入 Docker

接口测试此前默认使用 OrangeHRM 官方公共 Demo。公共环境适合学习请求结构，但数据会被其他用户修改，服务状态也不受本项目控制，并且无法直接连接数据库。Phase 6 使用 Docker Compose 在本机运行独立的 OrangeHRM 和 MariaDB，为稳定回归及后续数据库校验提供可重复环境。

## 当前架构

```text
Host: http://localhost:8080
              ↓ 8080:80
OrangeHRM 5.9 Container
              ↓ db:3306（Compose 内部网络）
MariaDB 10.11.19 Container
```

数据库端口没有暴露到宿主机。OrangeHRM 通过 Compose 服务名 `db` 访问 MariaDB，只有 Web 服务通过宿主机端口 `8080` 对外提供访问。

## Image 来源与版本

- OrangeHRM：`orangehrm/orangehrm:5.9`，来自 [OrangeHRM 官方 Docker Hub 仓库](https://hub.docker.com/r/orangehrm/orangehrm/tags)。固定 `5.9` 而不使用 `latest`，避免未来拉取到不同版本；其内容可与 [OrangeHRM 官方 v5.9 Dockerfile](https://github.com/orangehrm/orangehrm/blob/v5.9/Dockerfile) 对照。
- 数据库：`mariadb:10.11.19`，来自 [MariaDB Docker Official Image](https://hub.docker.com/_/mariadb)。[OrangeHRM 5.9 官方 release](https://github.com/orangehrm/orangehrm/releases/tag/v5.9) 声明支持 MariaDB 5.5 至 12.0，10.11 是长期维护系列；固定补丁版本便于复现。

OrangeHRM 镜像内的 Apache 实际暴露 `80/tcp`，因此 Compose 使用 `8080:80`，左侧是 host port，右侧是 container port。

## 准备 `.env`

复制示例文件：

```powershell
Copy-Item .env.example .env
```

修改 `.env` 中所有 password placeholder，只保存本地环境使用的密码。`.env` 已被 `.gitignore` 忽略，不能提交；`.env.example` 只保存变量名和安全占位值。

Compose 会自动读取 `.env` 做变量替换，但不会把其中的变量自动导出到当前 PowerShell，也不会自动提供给 pytest。

## 启动与初始化

检查配置并启动：

```powershell
docker compose config --quiet
docker compose up -d
docker compose ps
```

首次启动时，MariaDB 会创建空的 `orangehrm` 数据库和专用用户。Compose 等待数据库 healthcheck 通过后再启动 OrangeHRM。

官方 OrangeHRM image 不会根据环境变量自动安装。首次访问会进入安装向导。本项目实际使用镜像提示的新版 CLI 初始化：

```powershell
docker compose exec orangehrm sh -lc "cd /var/www/html && php installer/console install:on-existing-database"
```

关键输入如下：

- Database Host Name：`db`
- Database Host Port：`3306`
- Database Name / Username / Password：使用 `.env` 中对应的本地值
- Existing Database：使用 Compose 已创建的空数据库
- Organization：`OrangeHRM Quality Lab`
- Country：`china`
- Language：`en_US`
- Timezone：`Asia/Shanghai`
- Admin Username / Password：使用 `.env` 中的本地管理员配置
- Registration：本地学习环境选择 `no`

安装完成后访问：

```text
http://localhost:8080
```

正常情况下根地址会跳转到 `/web/index.php/auth/login`，而不是再次进入 `/installer/`。

## 状态、日志与停止

```powershell
docker compose ps
docker compose logs --tail 100
docker compose logs orangehrm
docker compose logs db
docker compose down
```

普通 `docker compose down` 会删除容器和 Compose 网络，但不会删除 named volume。不要使用 `docker compose down -v`，除非明确要彻底清空本地安装和数据库。

## Named volume

- `orangehrm_quality_lab_db_data` → `/var/lib/mysql`：保存 MariaDB 数据。
- `orangehrm_quality_lab_app_data` → `/var/www/html`：保存 OrangeHRM 安装器生成的配置及当前 5.9 应用目录。

Container 可以停止、删除和重新创建；volume 生命周期独立，因此 down/up 后仍能恢复已安装环境。OrangeHRM image 本身声明整个 `/var/www/html` 为 volume，如果不显式命名，重建容器后新的匿名 volume 不会自动复用原安装状态。

应用 volume 会覆盖新 image 中相同目录。未来升级 OrangeHRM 版本时不能只修改 image tag，需要单独设计应用文件与数据库的迁移；这不属于 Phase 6。

查看 volume：

```powershell
docker volume ls
docker volume inspect orangehrm_quality_lab_db_data
docker volume inspect orangehrm_quality_lab_app_data
```

## 让现有 pytest 使用本地环境

现有测试默认仍使用官方公共 Demo。要切换到本地环境，在运行测试的同一个 PowerShell 中设置：

```powershell
$env:ORANGEHRM_BASE_URL = "http://localhost:8080"
$env:ORANGEHRM_USERNAME = "Admin"
$env:ORANGEHRM_PASSWORD = "<本地管理员密码>"
.\.venv\Scripts\python.exe -B -m pytest -m smoke -v -p no:cacheprovider
```

`ORANGEHRM_BASE_URL` 不要添加末尾 `/`。Compose 使用的 `.env` 不会自动进入 pytest 进程，所以这三个变量需要显式设置。

## 常见排查点

1. **安装 Docker Desktop 后仍找不到 `docker`**：旧终端可能保留安装前的 PATH。重新打开终端或 Codex；如果临时直接调用 Docker 安装目录中的 CLI，也要确保同目录下的 credential helper 在 PATH 中。
2. **启动后看到安装页**：这是官方 image 的正常首次启动行为，不是服务失败。使用 Web Installer 或新版 `installer/console`；不要把已弃用的 `installer/cli_install.php` 当作帮助命令运行，它会直接读取示例配置并尝试安装。
3. **修改 `.env` 后数据库账号没有变化**：MariaDB 初始化变量只在数据目录为空时生效。保留 DB volume 时，修改 `.env` 不会重建已有用户或密码。

日志中的 Apache `ServerName` 提示和 Docker Desktop 环境下 MariaDB 的 `io_uring` 回退是本轮观察到的非阻塞警告；应结合 healthcheck、`mysqld is alive`、HTTP 页面和测试结果判断服务是否可用。
