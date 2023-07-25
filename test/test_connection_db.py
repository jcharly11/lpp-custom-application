import unittest
import sqlite3

from src.database.db_config import DB_NAME

class test_ConnectionDB(unittest.TestCase):

    def test_Connection(self):
        expected = True
        connection = sqlite3.connect(DB_NAME)
        actual= False 
        if connection is not None:
            actual=True

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main

