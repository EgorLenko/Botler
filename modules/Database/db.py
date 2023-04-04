import sqlite3


class Database:
    TEST_USER_DB = 'test_user.db'

    def __init__(self, db_name: str):
        if db_name and isinstance(db_name, str):
            if db_name.find('.') != -1:
                self.name = db_name.split('.')[0]
            else:
                self.name = db_name
        else:
            raise ValueError('Provided incorrect database name. db_name must be a string')
        self.connection = self.get_connection(self.name)
        self.cursor = self.connection.cursor()

    @classmethod
    def get_connection(cls, name: str):
        try:
            if name.lower() in ('user', 'test_user', 'users'):
                return sqlite3.connect(cls.TEST_USER_DB)
            else:
                return sqlite3.connect(name) if '.' in name else sqlite3.connect(f'{name}.db')
        except* TypeError as type_e:
            print(f'Database {type_e.exceptions} -> database name (db_name) must be a string: {type_e.message}')
        except* ValueError as value_e:
            print(f'Database {value_e.exceptions} -> calling database without providing a name {value_e.message}')

    def __create_user_table(self, table_name: str):
        if not self.connection:
            raise Exception('Connection error')
        if table_name and isinstance(table_name, str):
            self.cursor.execute(f"""CREATE TABLE {table_name}
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            telegram_id INTEGER,
                            first_name TEXT,
                            last_name TEXT,
                            username TEXT,
                            is_bot BOOLEAN)
                        """)
        else:
            raise Exception('Please provide a table name (table_name: str)')

