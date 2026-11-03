"""Schema temporer untuk QA browser/launcher, terpisah dari prefix konfigurasi pengguna."""
from contextlib import contextmanager
from dataclasses import replace
import re
import uuid

from labcore.catalog import LABS
from labcore.dbconfig import load_settings
from labcore.mysql_backend import raw_connection


@contextmanager
def temporary_mysql(config_file):
    settings = replace(load_settings('mysql',config_file), prefix='qa_' + uuid.uuid4().hex[:12])
    raw_connection(settings).close()
    try:
        yield settings
    finally:
        # Daftar nama berasal dari katalog tetap, bukan enumeration/drop wildcard.
        schemas = [settings.prefix + '_' + scope for scope in ['dashboard', *[lab['id'] for lab in LABS]]]
        connection = raw_connection(settings)
        try:
            with connection.cursor() as cursor:
                for schema in schemas:
                    if not re.fullmatch(r'qa_[a-f0-9]{12}_[a-z0-9_]+',schema):
                        raise RuntimeError('Nama schema QA tidak valid.')
                    cursor.execute(f'DROP DATABASE IF EXISTS `{schema}`')
        finally:
            connection.close()
