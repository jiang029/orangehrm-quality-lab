import os
from urllib.parse import urlparse

import pytest

from utils.db import create_connection


@pytest.fixture(scope="session", autouse=True)
def require_local_database_environment():
    """阻止 DB tests 把公共 Demo API 与本地数据库混合使用。"""

    required_variables = (
        "ORANGEHRM_BASE_URL",
        "ORANGEHRM_USERNAME",
        "ORANGEHRM_PASSWORD",
        "ORANGEHRM_DB_NAME",
        "ORANGEHRM_DB_USER",
        "ORANGEHRM_DB_PASSWORD",
    )
    missing_variables = [
        variable_name
        for variable_name in required_variables
        if not os.getenv(variable_name)
    ]
    if missing_variables:
        missing_text = ", ".join(missing_variables)
        pytest.skip(f"本地数据库测试缺少环境变量: {missing_text}")

    local_hosts = {"127.0.0.1", "localhost", "::1"}
    api_host = urlparse(os.environ["ORANGEHRM_BASE_URL"]).hostname
    database_host = os.getenv("ORANGEHRM_DB_HOST", "127.0.0.1")
    if api_host not in local_hosts or database_host not in local_hosts:
        pytest.skip("db marker 只允许连接本机 OrangeHRM 与 MariaDB")


@pytest.fixture(scope="function")
def db_connection():
    """为每条数据库测试提供独立连接，并在结束后关闭。"""

    # DB tests 只在显式提供本地数据库配置时运行；缺少配置属于未选择该环境，
    # 使用 skip 不会影响仍可独立运行的公共 Demo API tests。
    try:
        connection = create_connection()
    except RuntimeError as error:
        pytest.skip(str(error))

    # function scope 避免三条测试共享连接状态；yield 后统一释放 TCP 连接。
    yield connection
    connection.close()
