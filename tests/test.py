# 这是一个用例示例，展示了如何使用 NoraORM 来进行同步和异步的数据库操作
class NoraORMUseCases:
    def __init__(self, orm):
        self.orm = orm

    # 同步用例
    def insert_user_sync(self, username, email):
        self.orm.test_insert_user_sync(self.orm, username, email)

    def get_user_sync(self, username):
        return self.orm.test_get_user_sync(self.orm, username)

    def update_user_email_sync(self, username, new_email):
        self.orm.test_update_user_email_sync(self.orm, username, new_email)

    def delete_user_sync(self, username):
        self.orm.test_delete_user_sync(self.orm, username)

    # 异步用例
    def insert_user_async(self, username, email):
        self.orm.test_insert_user_async(self.orm, username, email)

    def get_user_async(self, username):
        self.orm.test_get_user_async(self.orm, username)

    def update_user_email_async(self, username, new_email):
        self.orm.test_update_user_email_async(self.orm, username, new_email)

    def delete_user_async(self, username):
        self.orm.test_delete_user_async(self.orm, username)

    # 使用查询条件
    def get_users_with_condition(self, condition, value):
        sql = f'SELECT * FROM users WHERE {condition}'
        return self.orm.execute_sync('execute', args=(sql, (value,))).fetchall()

# 实例化 NoraORMUseCases 并调用方法执行数据库操作
# orm_instance 应该是你的 NoraORM 实例
use_cases = NoraORMUseCases(orm_instance)
