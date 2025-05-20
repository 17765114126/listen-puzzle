import sqlite3
from typing import Optional, Type, TypeVar, Dict, Any
import os

T = TypeVar('T')


def generate_class_from_table(table_name: str, db_path: str) -> Type[T]:
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取表的列信息
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()

    # 构建类的字段和类型
    fields = {}
    for column_info in columns_info:
        col_name = column_info[1]
        col_type = column_info[2]

        # 将SQLite类型映射到Python类型
        if col_type.startswith('INT') or col_type.startswith('INTEGER'):
            field_type = Optional[int]
        elif col_type.startswith('TEXT'):
            field_type = Optional[str]
        elif col_type.startswith('REAL') or col_type.startswith('FLOAT'):
            field_type = Optional[float]
        elif col_type.startswith('TIMESTAMP'):
            field_type = Optional[str]  # 或者使用datetime类型
        elif col_type.startswith('TINYINT'):
            field_type = Optional[bool]  # 假设TINYINT用于布尔值
        else:
            field_type = Optional[Any]  # 默认类型

        fields[col_name] = (field_type, column_info[4])  # col_info[4] 是默认值

    # 关闭数据库连接
    conn.close()

    # 构建类定义
    class_definition = f"class {table_name.capitalize()}(BaseModel):\n"
    class_definition += f"    table_name: str = \"{table_name}\"\n"
    for col_name, (field_type, default_value) in fields.items():
        if default_value != 'NULL':
            class_definition += f"    {col_name}: {field_type.__name__}[{field_type.__args__[0].__name__}] = {default_value}\n"
        else:
            class_definition += f"    {col_name}: {field_type.__name__}[{field_type.__args__[0].__name__}] = None\n"
    return class_definition


# 使用示例


if __name__ == '__main__':
    db_path = os.path.join('..', 'db', 'we_library.db')

    table_list = ["chat_role"]
    for table in table_list:
        Tag = generate_class_from_table(table, db_path)
        print(Tag)
