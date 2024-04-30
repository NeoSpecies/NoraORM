import sqlite3
import queue
import threading
import atexit
from sqlite3 import Error, Connection, Cursor
from typing import Optional, List, Dict, Any, Tuple


class DatabaseOperation:
    def __init__(self, method, args, kwargs, callback=None, sync_event=None):
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.sync_event = sync_event
        self.result = None
        self.exception = None


class DatabaseWorker(threading.Thread):
    def __init__(self, db_instance):
        super(DatabaseWorker, self).__init__()
        self.db_instance = db_instance
        self.queue = queue.Queue()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            db_operation = self.queue.get()
            if db_operation is None:
                break
            try:
                result = getattr(self.db_instance, db_operation.method)(*db_operation.args, **db_operation.kwargs)
                db_operation.result = result
            except Exception as e:
                db_operation.exception = e
                print(f"Error: {e}")
            finally:
                if db_operation.sync_event:
                    db_operation.sync_event.set()
                if db_operation.callback:  # 调用回调函数
                    db_operation.callback(db_operation.result, db_operation.exception)  # 传递结果和异常
                self.queue.task_done()

    def perform(self, db_operation):
        self.queue.put(db_operation)

    def close(self):
        self.queue.put(None)
        self.queue.join()


class NoraORM:
    def __init__(self, db_path):
        self.conn_pool = sqlite3.connect(db_path, check_same_thread=False)
        self.worker = DatabaseWorker(self)
        atexit.register(self.shutdown)  # 确保在解释器退出时调用 shutdown

    def shutdown(self):
        self.worker.close()
        self.conn_pool.close()

    def get_connection(self) -> Connection:
        return self.conn_pool

    def release_connection(self, conn: Connection):
        pass

    def generate_fields(self, fields: Optional[List[str]] = None) -> str:
        """
        Generates a string of fields for SQL queries.

        :param fields: Optional list of field names. If None, defaults to "*".
        :return: A string of comma-separated field names.
        """
        return ", ".join(fields) if fields else "*"

    def generate_conditions(self, conditions: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
        """
        Generates SQL condition strings and values from a dictionary
        supporting complex conditions with comparison operators and logical operators.

        :param conditions: Dictionary of conditions.
        :return: A tuple of condition string and values list.
        """
        query_conditions = ""
        query_values: List[Any] = []
        if conditions:
            condition_list = []
            for key, value in conditions.items():
                # 解析字段和操作符，字段格式可以是 "field[operator]"
                field, operator = key.strip("[]").split("[") if "[" in key and "]" in key else (key, "=")

                # 对于值为列表的情况，处理IN查询
                if isinstance(value, list) and operator.upper() in ["IN", "NOT IN"]:
                    placeholders = ", ".join("?" for _ in value)
                    condition_list.append(f"{field} {operator} ({placeholders})")
                    query_values.extend(value)
                else:
                    condition_list.append(f"{field} {operator} ?")
                    query_values.append(value)

            query_conditions = " WHERE " + " AND ".join(condition_list)
        return query_conditions, query_values

    def pdo_get(self, table: str, fields: Optional[List[str]] = None, conditions: Optional[Dict[str, Any]] = None) -> \
            Optional[List[Dict[str, Any]]]:
        """
        Fetches records from the database based on conditions.

        :param table: Table name.
        :param fields: Optional list of fields to fetch.
        :param conditions: Optional dictionary of conditions.
                           You can include an "ORDER BY" key with a list of dictionaries specifying the fields and sort order.
                           Example: {"ORDER BY": [{"name": "desc"}, {"id": "asc"}]}
        :return: List of dictionaries representing fetched rows, where keys are field names.
        """
        field_str = self.generate_fields(fields)
        order_by_list = conditions.get("ORDER BY", [])
        conditions.pop("ORDER BY", None)  # 删除条件字典中的"ORDER BY"键

        condition_str, condition_values = self.generate_conditions(conditions)  # 需根据新的conditions生成条件字符串和值

        order_by_str = ""
        if order_by_list:
            order_by_clauses = []
            for order_by_dict in order_by_list:
                for field, sort_order in order_by_dict.items():
                    order_by_clauses.append(f"{field} {sort_order.upper()}")

            if order_by_clauses:
                order_by_str = " ORDER BY " + ", ".join(order_by_clauses)

        query = f"SELECT {field_str} FROM {table}{condition_str}{order_by_str}"

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, condition_values)
                result = cursor.fetchall()

                # 获取字段名列表
                field_names = [desc[0] for desc in cursor.description]

                # 构建结果字典列表
                formatted_result = []
                for row in result:
                    row_dict = dict(zip(field_names, row))
                    formatted_result.append(row_dict)

            return formatted_result
        except Error as e:
            print(f"Error executing SELECT query: {e}")
            return None

    def pdo_insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Inserts a new record into the database.

        :param table: Table name.
        :param data: Dictionary representing the data to insert.
        :return: ID of the inserted record.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = list(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                return cursor.lastrowid  # 返回插入记录的ID
        except Error as e:
            print(f"Error executing INSERT query: {e}")
            return -1  # 出现错误时返回 -1 或其他合适的错误代码

    def pdo_update(self, table: str, data: Dict[str, Any], conditions: Dict[str, Any]):
        """
        Updates records in the database based on conditions.

        :param table: Table name.
        :param data: Dictionary of fields to update.
        :param conditions: Dictionary of conditions to match records.
        """
        update_fields = ", ".join(f"{column} = ?" for column in data.keys())
        values = list(data.values())
        condition_str, condition_values = self.generate_conditions(conditions)
        query = f"UPDATE {table} SET {update_fields}{condition_str}"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values + condition_values)
                conn.commit()
                return cursor.rowcount  # 返回受影响的行数
        except Error as e:
            print(f"Error executing UPDATE query: {e}")

    def pdo_delete(self, table: str, conditions: Dict[str, Any]):
        """
        Deletes records from the database based on conditions.

        :param table: Table name.
        :param conditions: Dictionary of conditions to match records.
        """
        condition_str, condition_values = self.generate_conditions(conditions)
        query = f"DELETE FROM {table}{condition_str}"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, condition_values)
                conn.commit()
                return cursor.rowcount  # 返回受影响的行数
        except Error as e:
            print(f"Error executing DELETE query: {e}")

    # 使用队列执行操作
    def execute_in_queue(self, method: str, *args: Any, callback=None, **kwargs: Any):
        db_op = DatabaseOperation(method, args, kwargs, callback=callback)  # 传递回调函数
        self.worker.perform(db_op)

    # 同步执行操作
    def execute_sync(self, method: str, *args: Any, callback=None, **kwargs: Any) -> Any:
        sync_event = threading.Event()
        db_op = DatabaseOperation(method, args, kwargs, callback=callback, sync_event=sync_event)
        self.worker.perform(db_op)
        sync_event.wait()
        if db_op.exception:
            raise db_op.exception
        return db_op.result
