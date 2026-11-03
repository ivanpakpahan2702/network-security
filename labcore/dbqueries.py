"""Operasi dialek yang dipakai bersama, hanya identifier konstan milik aplikasi."""
import re


def identifier(value):
    if not re.fullmatch(r'[a-z_][a-z0-9_]*', value):
        raise ValueError('Identifier database tidak valid.')
    return '`' + value + '`'


def insert_missing(db, table, values, keys):
    columns = ','.join(identifier(name) for name in values)
    query = f'INSERT INTO {identifier(table)} ({columns}) VALUES ({",".join("?" for _ in values)})'
    if db.dialect == 'mysql':
        key = identifier(keys[0])
        query += f' ON DUPLICATE KEY UPDATE {key}={key}'
    else:
        query += f' ON CONFLICT({",".join(identifier(key) for key in keys)}) DO NOTHING'
    return db.execute(query, tuple(values.values()))


def upsert(db, table, values, keys, maximum=(), increment=(), timestamps=()):
    query = f'INSERT INTO {identifier(table)} ({",".join(identifier(name) for name in values)}) VALUES ({",".join("?" for _ in values)})'
    updates, parameters = [], list(values.values())
    for column, value in values.items():
        if column in keys:
            continue
        name = identifier(column)
        if column in maximum:
            operation = 'GREATEST' if db.dialect == 'mysql' else 'MAX'
            updates.append(f'{name}={operation}({name},?)')
        elif column in increment:
            updates.append(f'{name}={name}+?')
        else:
            updates.append(f'{name}=?')
        parameters.append(value)
    updates.extend(f'{identifier(name)}=CURRENT_TIMESTAMP' for name in timestamps)
    query += (' ON DUPLICATE KEY UPDATE ' if db.dialect == 'mysql' else
              f' ON CONFLICT({",".join(identifier(key) for key in keys)}) DO UPDATE SET ')
    return db.execute(query + ','.join(updates), tuple(parameters))


def begin_write(db, lock=None):
    if db.dialect == 'sqlite':
        db.execute('BEGIN IMMEDIATE')
    else:
        db.execute('START TRANSACTION')
        if lock:
            # Row lock serializes check-then-insert for this operation across connections.
            row = db.execute('SELECT name FROM lab_locks WHERE name=? FOR UPDATE', (lock,)).fetchone()
            if row is None:
                raise RuntimeError('Lock transaksi lab belum diinisialisasi.')


def query_display(db, query):
    if db.dialect == 'mysql':
        from labcore.mysql_backend import parameter_sql
        return parameter_sql(query)
    return query
