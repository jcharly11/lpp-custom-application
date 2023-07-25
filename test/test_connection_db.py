import unittest
import sqlite3
from database.db_config import DB_PATH


class test_connection_db(unittest.TestCase):
    def test_connection(self):
        expected = True
        actual = connectionDB()
        self.assertEqual(expected, actual)


def connectionDB(self):
        connection = sqlite3.connect(DB_PATH)
        if connection is not None:
            return True
        else:
            return False


if __name__ == '__main__':
    unittest.main

