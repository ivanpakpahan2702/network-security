r"""Jalankan suite perilaku yang sama pada MySQL/MariaDB, memakai schema qa_<acak>.

Wajib koneksi uji eksplisit; hanya schema yang dibuat suite ini yang dihapus.
User pengujian memerlukan CREATE/DROP/DML pada qa\_%.*; bukan kredensial produksi.
"""
import argparse
from dataclasses import replace
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from labcore.dbconfig import load_settings, target_for, MySQLTarget
from labcore.database import connect
from labcore.factory import create_app
from labcore.dashboard import create_dashboard
from labcore.mysql_backend import raw_connection
from tests import test_labs, test_advanced, test_learning, test_network


def mysql_case(base, module, settings):
    class MySQLCase(base):
        def setUp(self):
            self.mysql_settings = replace(settings, backend='mysql', prefix='qa_' + uuid.uuid4().hex[:12])
            self.mysql_targets, self.path_targets = set(), {}

            def register(path, scope):
                target = target_for(path, scope, self.mysql_settings)
                self.mysql_targets.add(target.schema)
                self.path_targets[Path(path).resolve()] = target

            def app_wrapper(lab_id, *args, **kwargs):
                directory = Path(kwargs['data_dir'])
                register(directory / 'lab.sqlite3', lab_id)
                return create_app(lab_id, *args, **kwargs, database_settings=self.mysql_settings)

            def dashboard_wrapper(*args, **kwargs):
                directory = Path(kwargs['data_dir'])
                register(directory / 'dashboard.sqlite3','dashboard')
                return create_dashboard(*args, **kwargs, database_settings=self.mysql_settings)

            def connect_wrapper(target):
                if not isinstance(target,MySQLTarget):
                    target = self.path_targets.get(Path(target).resolve(),target)
                return connect(target)

            self.addCleanup(self.drop_created_schemas)
            for name, replacement in (('create_app',app_wrapper),('create_dashboard',dashboard_wrapper),('connect',connect_wrapper)):
                if hasattr(module,name):
                    patcher = patch.object(module,name,replacement)
                    patcher.start()
                    self.addCleanup(patcher.stop)
            super().setUp()

        def drop_created_schemas(self):
            if not self.mysql_targets:
                return
            connection = raw_connection(self.mysql_settings)
            try:
                with connection.cursor() as cursor:
                    for schema in self.mysql_targets:
                        if not re.fullmatch(r'qa_[a-f0-9]{12}_[a-z0-9_]+',schema) or not schema.startswith(self.mysql_settings.prefix+'_'):
                            raise RuntimeError('Scope cleanup schema tidak valid.')
                        cursor.execute(f'DROP DATABASE IF EXISTS `{schema}`')
            finally:
                connection.close()
    MySQLCase.__name__ = 'MySQL' + base.__name__
    MySQLCase.__qualname__ = MySQLCase.__name__
    return MySQLCase


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db-config',type=Path,required=True)
    parser.add_argument('--match',help='Hanya jalankan nama tes yang mengandung teks ini')
    args = parser.parse_args()
    settings = load_settings('mysql',args.db_config)
    raw_connection(settings).close()
    suite = unittest.TestSuite()
    for base, module in ((test_labs.LabTests,test_labs),(test_advanced.AdvancedTests,test_advanced),
                         (test_learning.LearningTests,test_learning),(test_network.NetworkTests,test_network)):
        cases = unittest.defaultTestLoader.loadTestsFromTestCase(mysql_case(base,module,settings))
        suite.addTests(test for test in cases if not args.match or args.match in test.id())
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
