# NoraORM: Asynchronous SQLite Database Operations

## Introduction

NoraORM is an asynchronous object-relational mapping (ORM) system for Python, designed to work with SQLite databases. It leverages threading and queueing mechanisms to enable non-blocking database interactions within your applications. This ORM allows you to perform database operations without having to manage threads or worry about the complexities of asynchronous programming.

## Features

- **Asynchronous Operations:** Run database operations without blocking the main thread, improving performance for I/O-bound applications.
- **Threading and Queueing:** Uses a background thread to handle database operations, placing them in a queue for execution in the order received.
- **Callback Support:** Provides a callback mechanism to execute custom functions upon the completion of database operations.
- **Thread-Safe Connections:** Configured to allow SQLite connections to be used across multiple threads.
- **Graceful Shutdown:** Ensures that all database operations are completed before the program exits, preventing data loss or corruption.

## Installation

To use NoraORM in your project, simply clone the repository from GitHub:

```sh
git clone https://github.com/your-username/noraorm.git
```

Then, install it using `pip`:

```sh
pip install ./noraorm
```

## Usage Example

Here's a basic example of how you can use NoraORM to interact with your SQLite database:

```python
from noraorm import NoraOrm

# Initialize the ORM
db = NoraOrm('my_database.db')

# Define a callback function
def on_insert_complete(result):
    print("Insert operation completed with result:", result)

# Asynchronous Insert
db.insert('INSERT INTO my_table (column1, column2) VALUES (?, ?)', 
          (value1, value2), 
          callback=on_insert_complete)

# Update and Delete can be used similarly
db.update('UPDATE my_table SET column1 = ? WHERE column2 = ?', 
          (new_value, condition_value))

db.delete('DELETE FROM my_table WHERE column1 = ?', (value_to_delete,))

# To ensure graceful shutdown
db.shutdown()
```

## Documentation

For complete documentation, including a list of all available methods and their parameters, please refer to the `docs` directory in the repository.

## Notes and Considerations

- **Database Connection:** The ORM uses a single connection object; ensure that your database operations are thread-safe.
- **Error Handling:** It's important to implement proper error handling in your callback functions to deal with any database operation errors.
- **Performance:** While the ORM helps avoid blocking the main thread, the actual performance gain depends on the nature of your application and the database size.
- **Logging:** It's recommended to set up logging for your application to capture any issues that might occur during database operations.

## Contributing

We welcome contributions! If you have ideas for improvement or have found a bug, please open an issue or submit a pull request on GitHub.

## License

NoraORM is licensed under the MIT License. See the LICENSE file for more details.

---
