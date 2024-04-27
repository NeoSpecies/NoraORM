# NoraORM：异步SQLite数据库操作

## 介绍

NoraORM 是一个为 Python 设计的异步对象关系映射（ORM）系统，旨在与 SQLite 数据库一起工作。它利用线程和队列机制来启用应用程序中的非阻塞数据库交互。该 ORM 允许您执行数据库操作，而无需管理线程或担心异步编程的复杂性。

## 特性

- **异步操作：** 运行数据库操作时不会阻塞主线程，提高 I/O 密集型应用程序的性能。
- **线程与队列：** 使用后台线程处理数据库操作，将它们放入队列中按收到的顺序执行。
- **回调支持：** 提供回调机制在数据库操作完成后执行自定义函数。
- **线程安全连接：** 配置允许在多个线程中使用 SQLite 连接。
- **优雅关闭：** 确保在程序退出前完成所有数据库操作，防止数据丢失或损坏。

## 安装

要在您的项目中使用 NoraORM，只需从 GitHub 克隆库：

```sh
git clone https://github.com/your-username/noraorm.git
```

然后，使用 `pip` 进行安装：

```sh
pip install ./noraorm
```

## 使用示例

以下是一个基本示例，展示了如何使用 NoraORM 与您的 SQLite 数据库交互：

```python
from noraorm import NoraOrm

# 初始化 ORM
db = NoraOrm('my_database.db')

# 定义一个回调函数
def on_insert_complete(result):
    print("插入操作完成，结果为：", result)

# 异步插入
db.insert('INSERT INTO my_table (column1, column2) VALUES (?, ?)', 
          (value1, value2), 
          callback=on_insert_complete)

# 更新和删除操作可以类似地使用
db.update('UPDATE my_table SET column1 = ? WHERE column2 = ?', 
          (new_value, condition_value))

db.delete('DELETE FROM my_table WHERE column1 = ?', (value_to_delete,))

# 确保优雅关闭
db.shutdown()
```

## 文档

有关所有可用方法及其参数的完整文档，请参阅库中的 `docs` 目录。

## 注意事项和考虑因素

- **数据库连接：** ORM 使用单个连接对象；确保您的数据库操作是线程安全的。
- **错误处理：** 在您的回调函数中实现适当的错误处理非常重要，以处理任何数据库操作错误。
- **性能：** 虽然 ORM 帮助避免了主线程的阻塞，但实际性能提升取决于您的应用程序性质和数据库大小。
- **日志记录：** 建议为您的应用程序设置日志记录，以捕获数据库操作过程中可能发生的任何问题。

## 贡献

我们欢迎贡献！如果您有改进建议或发现了错误，请在 GitHub 上开一个问题或提交一个拉取请求。

## 许可证

NoraORM 采用 MIT 许可证。有关更多详情，请查看许可证文件。

---
