import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from labcore.dbconfig import DatabaseSettings, MySQLTarget, load_settings, target_for
from labcore.mysql_backend import parameter_sql


class DatabaseConfigurationTests(unittest.TestCase):
    def test_factory_target_default_is_sqlite_and_mysql_is_explicit(self):
        path = Path('instance/lab.sqlite3')
        self.assertEqual(target_for(path,'01_sql_injection'),path)
        settings = DatabaseSettings(backend='mysql',password='PRIVATE-PASSWORD')
        target = target_for(path,'01_sql_injection',settings)
        self.assertIsInstance(target,MySQLTarget)
        self.assertEqual(target.schema,'security_lab_01_sql_injection')
        self.assertNotIn('PRIVATE-PASSWORD',repr(target))
        self.assertNotIn('PRIVATE-PASSWORD',repr(settings))

    def test_config_precedence_and_invalid_config_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'db.toml'
            path.write_text('[database]\nbackend="mysql"\n[mysql]\nport=13316\npassword="from-file"\nprefix="kelas_b"\n',encoding='utf-8')
            with patch.dict(os.environ,{'SECURITY_LAB_MYSQL_PASSWORD':'from-env'}):
                settings = load_settings(config_file=path)
                self.assertEqual((settings.backend,settings.port,settings.prefix,settings.password),('mysql',13316,'kelas_b','from-env'))
                self.assertEqual(load_settings('sqlite',path).backend,'sqlite')
            with self.assertRaises(ValueError):
                load_settings('mysql',Path(directory)/'missing.toml')
            path.write_text('[mysql]\npassword="UNTERMINATED',encoding='utf-8')
            with self.assertRaises(ValueError) as caught:
                load_settings('mysql',path)
            self.assertNotIn('UNTERMINATED',str(caught.exception))

    def test_mysql_identifiers_and_port_are_validated(self):
        for values in ({'prefix':'x`; DROP DATABASE other;--'},{'prefix':'x'*21},{'prefix':123},{'port':True},{'port':0},{'port':65536},{'host':[]},{'backend':'oracle'}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                DatabaseSettings(**values)
        with self.assertRaises(ValueError):
            target_for(Path('x'),'../other',DatabaseSettings(backend='mysql'))

    def test_placeholders_do_not_rewrite_literals_or_comments(self):
        query = "SELECT '?' AS literal, '50%' AS percent, `a?` FROM t WHERE name=? AND note='it''s ?' /* ? */ -- ?\n AND id=?"
        converted = parameter_sql(query)
        self.assertIn("'?' AS literal",converted)
        self.assertIn("'50%%' AS percent",converted)
        self.assertIn("note='it''s ?'",converted)
        self.assertIn('/* ? */ -- ?\n',converted)
        self.assertEqual(converted.count('%s'),2)
        self.assertEqual(parameter_sql("SELECT ? # ?\n, ?"),'SELECT %s # ?\n, %s')


if __name__ == '__main__':
    unittest.main()
