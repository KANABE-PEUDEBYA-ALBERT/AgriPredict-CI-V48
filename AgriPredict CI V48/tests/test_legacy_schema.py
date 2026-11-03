import sqlite3
import unittest
from migrations.legacy_schema import ensure_legacy_columns


class LegacySchemaTests(unittest.TestCase):
    def test_adds_missing_columns_without_losing_rows(self):
        connection = sqlite3.connect(':memory:')
        connection.executescript('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password_hash TEXT);
            CREATE TABLE farms (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, region TEXT);
            CREATE TABLE plots (id INTEGER PRIMARY KEY, farm_id INTEGER, name TEXT, area_ha REAL, product TEXT);
            CREATE TABLE tasks (id INTEGER PRIMARY KEY, plot_id INTEGER, title TEXT);
            CREATE TABLE market_prices (id INTEGER PRIMARY KEY, observed_on TEXT, product TEXT, market TEXT, price_fcfa_kg REAL);
            INSERT INTO users(id,name,email,password_hash) VALUES(1,'Test','test@example.com','hash');
            INSERT INTO plots(id,farm_id,name,area_ha,product) VALUES(1,1,'Champ test',2,'Riz');
        ''')
        ensure_legacy_columns(connection)
        ensure_legacy_columns(connection)  # la migration doit pouvoir être rejouée
        columns = {row[1] for row in connection.execute('PRAGMA table_info(plots)')}
        self.assertTrue({'latitude','longitude','geometry_geojson','area_gps_ha','gps_accuracy','location_updated_at'} <= columns)
        self.assertEqual(connection.execute('SELECT name, area_ha FROM plots WHERE id=1').fetchone(), ('Champ test', 2.0))
        self.assertEqual(connection.execute("SELECT role FROM users WHERE id=1").fetchone(), ('producer',))
        connection.close()


if __name__ == '__main__':
    unittest.main()
