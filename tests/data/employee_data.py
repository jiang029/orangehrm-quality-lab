import json
import string
import time
from pathlib import Path

from faker import Faker


# 使用英文区域的姓名数据，再在下方过滤字符范围。这样既让 Faker 负责提供
# 多样化姓名，也能避免撇号、连字符或非 ASCII 字符让公共 Demo 偶发失败。
fake = Faker("en_US")

# Windows 的 time.time_ns() 以纳秒为单位返回数值，但系统时钟精度不一定达到纳秒。
# 这个集合只记录当前 Python 进程已经生成过的 Employee ID，用于处理极短时间内
# 得到相同时间戳的情况；它不承担跨进程或跨机器的全局唯一性职责。
_generated_employee_ids = set()


def _keep_ascii_letters(name):
    """只保留姓名中的 ASCII 字母，并为极端空结果提供安全兜底。"""

    ascii_name = "".join(
        character for character in name if character in string.ascii_letters
    )
    if ascii_name:
        return ascii_name

    # en_US 姓名清洗后通常不会为空；兜底仍由 Faker 生成固定长度的 ASCII 字母，
    # 避免极端数据使一个原本合法的基础 payload 变成空姓名。
    return fake.lexify(text="????????", letters=string.ascii_letters)


def _build_employee_id():
    """根据时间戳生成 10 位 Employee ID，并避免当前进程内重复。"""

    employee_id_number = time.time_ns() % 10_000_000_000

    # 如果系统时钟暂时返回相同值，就逐个顺延，直到找到本进程尚未用过的数字。
    # 测试规模很小，直接使用 set 做成员检查比引入锁或专门 ID 框架更容易理解。
    while employee_id_number in _generated_employee_ids:
        employee_id_number = (employee_id_number + 1) % 10_000_000_000

    _generated_employee_ids.add(employee_id_number)
    # zfill 补齐可能出现的前导 0，确保发送给接口的始终是 10 位字符串。
    return str(employee_id_number).zfill(10)


def build_employee_data(**overrides):
    """生成一份合法的 Create Employee payload，并允许按场景覆盖字段。"""

    # Factory 存在的原因是把“拿什么数据测”从测试步骤中分离出来：
    # Faker 负责生成多样化姓名，时间戳负责生成不易与公共 Demo 冲突的 Employee ID。
    employee_data = {
        "firstName": _keep_ascii_letters(fake.first_name()),
        "middleName": "",
        "lastName": _keep_ascii_letters(fake.last_name()),
        # 时间戳提供动态基础值，进程内去重处理系统时钟精度不足造成的重复；
        # 10 位长度沿用当前接口已验证可接受的 Employee ID 格式。
        "employeeId": _build_employee_id(),
        "empPicture": None,
    }

    # **overrides 收集调用方传入的关键字参数；dict.update 用这些值覆盖合法默认值。
    # 例如 firstName="" 可复用同一份基础结构构造必填字段异常输入。
    employee_data.update(overrides)

    # Factory 只负责返回输入数据，不发送请求也不做断言；接口调用和业务判断仍由
    # API 测试负责，避免数据模块同时承担多个职责。
    return employee_data


def load_employee_cases():
    """读取已确认的 Employee 固定 case，返回普通 Python list/dict。"""

    # Path(__file__) 从当前模块自身位置出发定位 JSON，不依赖命令在哪个目录执行。
    employee_cases_path = Path(__file__).with_name("employee_cases.json")

    # 数据流保持直接：JSON 文件 → json.load → Python list/dict → parametrize。
    # UTF-8 明确了读取编码，也为后续 case 中出现中文说明保留兼容性。
    with employee_cases_path.open(encoding="utf-8") as cases_file:
        return json.load(cases_file)
