import sqlite3
from contextlib import contextmanager
from fastapi import HTTPException


class SQLiteDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    @contextmanager
    def connect(self):
        """ 创建一个上下文管理器来自动处理数据库连接的打开和关闭 """
        try:
            self.connection = sqlite3.connect(self.db_name)
            yield self.connection
        finally:
            if self.connection:
                self.connection.close()

    def execute_query(self, query, params=None):
        """ 执行SQL语句（非查询）并提交更改 """
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()

    def fetch_count(self, query, params=None):
        # 将 * 替换为 COUNT(*)
        query = query.replace('*', 'COUNT(*)', 1)
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0

    def fetch_all(self, query, params=None):
        """ 执行查询语句并返回所有结果 """
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有行数据
            rows = cursor.fetchall()
            # 将行数据与列名组合成字典
            results = [dict(zip(columns, row)) for row in rows]
            return results

    def fetch_one(self, query, params=None):
        """ 执行查询语句并返回单个结果 """
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取单个行数据
            row = cursor.fetchone()
            if row is not None:
                # 将行数据与列名组合成字典
                result = dict(zip(columns, row))
                return result
            return None

    # 拼接 UPDATE sql
    @staticmethod
    def update_sql(req, tal_name):
        set_clauses = []
        params = []

        for field, value in req.dict().items():
            if value is not None and field not in ['id', "table_name"]:
                set_clauses.append(f"{field} = ?")
                params.append(value)

        if not set_clauses:
            raise HTTPException(status_code=400, detail="No fields to update")

        set_clause = ", ".join(set_clauses)
        sql_query = f"UPDATE {tal_name} SET {set_clause} WHERE id = ?"
        params.append(req.id)
        return sql_query, params

    # 拼接 insert sql
    @staticmethod
    def insert_sql(req, tal_name):
        columns = []
        values = []
        params = []

        for field, value in req.dict().items():
            if value is not None and field not in ['id', "table_name"]:
                columns.append(field)
                values.append("?")
                params.append(value)

        if not columns:
            raise HTTPException(status_code=400, detail="No fields to insert")

        column_list = ", ".join(columns)
        value_list = ", ".join(values)
        sql_query = f"INSERT INTO {tal_name} ({column_list}) VALUES ({value_list})"
        return sql_query, params

    # 添加或修改
    def add_or_update(self, req, tal_name):
        if req.id:
            sql_query, params = self.update_sql(req, tal_name)
        else:
            sql_query, params = self.insert_sql(req, tal_name)
        self.execute_query(sql_query, params)

    def page(self, req, tal_name):
        base_query = f"SELECT * FROM {tal_name}"
        params = []

        # 添加筛选条件
        where_clauses = []
        for field, value in req.dict().items():
            if value is not None and field not in ['table_name', 'page', 'page_size']:
                where_clauses.append(f"{field} LIKE ?")
                params.append(f"%{value}%")

            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

        # 获取总记录数
        count = self.fetch_count(base_query, tuple(params))

        # 添加分页
        if req.page_size != -1:
            base_query += " LIMIT ? OFFSET ?"
            params.extend([req.page_size, (req.page - 1) * req.page_size])

        return {
            "page": req.page,
            "page_size": req.page_size,
            "count": count,
            "data": self.fetch_all(base_query, tuple(params))
        }


# 使用示例
if __name__ == "__main__":
    db_name = 'test_db.db'
    db = SQLiteDB(db_name)

    # 创建表
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT '',
        age INTEGER DEFAULT 0,
        height REAL DEFAULT 0.0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT DEFAULT NULL,
        photo BLOB DEFAULT NULL
    );
    """
    db.execute_query(create_table_query)

    # 插入数据
    insert_data_query = """
    INSERT INTO test_table (name, age, height, is_active, description, photo)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    new_user = ('Alice', 25, 165.0, 1, 'This is Alice.', None)
    db.execute_query(insert_data_query, new_user)

    # 查询所有数据
    select_all_query = "SELECT * FROM test_table;"
    all_users = db.fetch_all(select_all_query)
    print(all_users)

    # 查询单条数据
    select_one_query = "SELECT * FROM test_table WHERE id=?;"
    user = db.fetch_one(select_one_query, (1,))
    print("User with ID 1:", user)

    # 更新数据
    update_data_query = """
    UPDATE test_table
    SET name=?, age=?, height=?, is_active=?, description=?, photo=?
    WHERE id=?;
    """
    updated_user = ('Alice Smith', 26, 165.0, 1, 'This is Alice, now with a last name!', None, 1)
    db.execute_query(update_data_query, updated_user)

    # 再次查询更新后的数据
    updated_user = db.fetch_one(select_one_query, (1,))
    print("Updated User with ID 1:", updated_user)

    # 删除数据
    # delete_data_query = "DELETE FROM test_table WHERE id=?;"
    # db.execute_query(delete_data_query, (1,))

    # 查询所有数据以确认删除
    # all_users = db.fetch_all(select_all_query)
    # print(all_users)
