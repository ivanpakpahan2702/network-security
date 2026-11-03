"""Adapter PyMySQL terbatas: parameter qmark, hasil seperti sqlite.Row, transaksi InnoDB.

SQL tanpa parameter (termasuk query rentan lab 01) dikirim apa adanya.
Tidak menerjemahkan dialek SQL atau mengubah input pengguna menjadi parameter.
"""
import re


def driver():
    try:
        import pymysql
    except ImportError:
        raise RuntimeError("Driver MySQL belum terpasang. Jalankan .venv\\Scripts\\python.exe -m pip install -r requirements-mysql.txt") from None
    return pymysql


def parameter_sql(query):
    """Ubah ? di luar literal/comment menjadi %s; lindungi % literal untuk DB-API."""
    result, state, index = [], None, 0
    while index < len(query):
        char = query[index]
        pair = query[index:index + 2]
        if state in ("'", '"', '`'):
            result.append('%%' if char == '%' else char)
            if char == '\\' and index + 1 < len(query):
                index += 1
                result.append('%%' if query[index] == '%' else query[index])
            elif char == state:
                if index + 1 < len(query) and query[index + 1] == state:
                    result.append(state)
                    index += 1
                else:
                    state = None
        elif state == 'line':
            result.append('%%' if char == '%' else char)
            if char == '\n':
                state = None
        elif state == 'block':
            result.append('%%' if char == '%' else char)
            if pair == '*/':
                result.append('/')
                index += 1
                state = None
        elif char in ("'", '"', '`'):
            state = char
            result.append(char)
        elif pair == '/*':
            state = 'block'
            result.append(pair)
            index += 1
        elif char == '#' or (pair == '--' and (index + 2 == len(query) or query[index + 2].isspace())):
            state = 'line'
            result.append(char)
        else:
            result.append('%s' if char == '?' else '%%' if char == '%' else char)
        index += 1
    return ''.join(result)


class Row:
    def __init__(self, columns, values):
        self._columns, self._values = columns, values

    def keys(self):
        return list(self._columns)

    def __getitem__(self, key):
        return self._values[self._columns.index(key)] if isinstance(key, str) else self._values[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)


class Result:
    def __init__(self, cursor):
        columns = tuple(column[0] for column in cursor.description) if cursor.description else ()
        self._rows = iter(Row(columns, values) for values in cursor.fetchall()) if columns else iter(())
        self.lastrowid, self.rowcount = cursor.lastrowid, cursor.rowcount

    def fetchone(self):
        return next(self._rows, None)

    def fetchall(self):
        return list(self._rows)

    def __iter__(self):
        return self._rows


def raw_connection(settings, schema=None):
    return driver().connect(host=settings.host, port=settings.port, user=settings.user,
                            password=settings.password, database=schema, charset='utf8mb4',
                            connect_timeout=5, read_timeout=15, write_timeout=15, autocommit=False,
                            local_infile=False, binary_prefix=True)


def prepare(target):
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', target.schema):
        raise ValueError('Nama schema MySQL tidak valid.')
    try:
        connection = raw_connection(target.settings, target.schema)
    except driver().err.OperationalError as error:
        if error.args[0] != 1049:
            raise
        connection = raw_connection(target.settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE IF NOT EXISTS `{target.schema}` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')
        finally:
            connection.close()
    else:
        connection.close()


class MySQLConnection:
    dialect = 'mysql'

    def __init__(self, target):
        self.connection = raw_connection(target.settings, target.schema)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED')
                cursor.execute("SET SESSION time_zone = '+00:00'")
        except Exception:
            self.connection.close()
            raise

    def execute(self, query, parameters=None):
        with self.connection.cursor() as cursor:
            cursor.execute(parameter_sql(query) if parameters is not None else query, parameters)
            return Result(cursor)

    def executemany(self, query, parameters):
        with self.connection.cursor() as cursor:
            cursor.executemany(parameter_sql(query), parameters)
            return Result(cursor)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.rollback() if exc_type else self.commit()
        finally:
            self.close()
