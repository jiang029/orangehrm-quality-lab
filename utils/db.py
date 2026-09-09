import os

import pymysql


DEFAULT_DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = 3307
REQUIRED_DB_ENV_VARS = (
    "ORANGEHRM_DB_NAME",
    "ORANGEHRM_DB_USER",
    "ORANGEHRM_DB_PASSWORD",
)


def create_connection():
    """根据运行环境创建返回字典行的 MariaDB 连接。"""

    missing_variables = [
        variable_name
        for variable_name in REQUIRED_DB_ENV_VARS
        if not os.getenv(variable_name)
    ]
    if missing_variables:
        missing_text = ", ".join(missing_variables)
        raise RuntimeError(f"数据库测试缺少环境变量: {missing_text}")

    port_text = os.getenv("ORANGEHRM_DB_PORT", str(DEFAULT_DB_PORT))
    try:
        port = int(port_text)
    except ValueError as error:
        raise ValueError("ORANGEHRM_DB_PORT 必须是整数") from error

    # DictCursor 让测试按列名读取结果，字段含义比依赖列顺序的 tuple 更清楚。
    return pymysql.connect(
        host=os.getenv("ORANGEHRM_DB_HOST", DEFAULT_DB_HOST),
        port=port,
        database=os.environ["ORANGEHRM_DB_NAME"],
        user=os.environ["ORANGEHRM_DB_USER"],
        password=os.environ["ORANGEHRM_DB_PASSWORD"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


def fetch_one(connection, sql, params=None):
    """执行参数化查询并返回一行；没有结果时返回 None。"""

    # with 会在成功或异常时都关闭 cursor；connection 由 fixture 统一关闭，
    # 这样查询函数只负责 SQL，资源生命周期仍能在测试结构中清楚看到。
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()
