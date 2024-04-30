当然，为了适应不同的应用场景，我们需要为`NoraORM`类提供同步和异步的查询方式。同时，也需要考虑不同的查询条件。以下是增删改查操作的同步和异步实现示例，以及条件查询的一些例子。

### 同步查询方案

#### 增（同步）

```python
def test_insert_user_sync(orm, username, email):
    sql = 'INSERT INTO users (username, email) VALUES (?, ?)'
    orm.execute_sync('execute', args=(sql, (username, email)))
```

#### 查（同步）

```python
def test_get_user_sync(orm, username):
    sql = 'SELECT * FROM users WHERE username = ?'
    result = orm.execute_sync('execute', args=(sql, (username,)))
    return result.fetchall()
```

#### 改（同步）

```python
def test_update_user_email_sync(orm, username, new_email):
    sql = 'UPDATE users SET email = ? WHERE username = ?'
    orm.execute_sync('execute', args=(sql, (new_email, username)))
```

#### 删（同步）

```python
def test_delete_user_sync(orm, username):
    sql = 'DELETE FROM users WHERE username = ?'
    orm.execute_sync('execute', args=(sql, (username,)))
```

### 异步查询方案

在异步方案中，我们通常会提供一个回调函数来处理结果。

#### 增（异步）

```python
def test_insert_user_async(orm, username, email):
    sql = 'INSERT INTO users (username, email) VALUES (?, ?)'
    orm.execute_in_queue('execute', args=(sql, (username, email)), callback=handle_result)
```

#### 查（异步）

```python
def test_get_user_async(orm, username):
    sql = 'SELECT * FROM users WHERE username = ?'
    orm.execute_in_queue('execute', args=(sql, (username,)), callback=handle_result)
```

#### 改（异步）

```python
def test_update_user_email_async(orm, username, new_email):
    sql = 'UPDATE users SET email = ? WHERE username = ?'
    orm.execute_in_queue('execute', args=(sql, (new_email, username)), callback=handle_result)
```

#### 删（异步）

```python
def test_delete_user_async(orm, username):
    sql = 'DELETE FROM users WHERE username = ?'
    orm.execute_in_queue('execute', args=(sql, (username,)), callback=handle_result)
```

### 查询条件介绍

查询条件通常涉及以下内容：

- **等于** (`=`): `SELECT * FROM users WHERE id = 1`
- **不等于** (`<>` or `!=`): `SELECT * FROM users WHERE username <> 'admin'`
- **大于** (`>`): `SELECT * FROM users WHERE id > 10`
- **小于** (`<`): `SELECT * FROM users WHERE id < 10`
- **大于等于** (`>=`): `SELECT * FROM users WHERE id >= 10`
- **小于等于** (`<=`): `SELECT * FROM users WHERE id <= 10`
- **IN** (在范围内): `SELECT * FROM users WHERE username IN ('user1', 'user2')`
- **NOT IN** (不在范围内): `SELECT * FROM users WHERE username NOT IN ('admin', 'guest')`
- **BETWEEN** (在两个值之间): `SELECT * FROM users WHERE created_at BETWEEN '2021-01-01' AND '2021-12-31'`
- **LIKE** (模糊匹配): `SELECT * FROM users WHERE username LIKE 'Joh%'`
- **NOT LIKE** (不模糊匹配): `SELECT * FROM users WHERE username NOT LIKE 'adm%'`
- **ORDER BY** (排序): `SELECT * FROM users ORDER BY created_at DESC`

每个查询条件都可以结合同步或异步查询方法使用。

```python
def handle_result(result):
    # ...处理查询结果...
    pass
```

在异步查询中，`handle_result`是一个回调函数，用于在查询完成后处理结果。它需要根据实际需求定义。

请注意，异步查询不会立即返回结果，而是将结果传递给回调函数。这对于不希望阻塞主线程的应用程序非常有用，比如在GUI应用程序或网络请求处理中。