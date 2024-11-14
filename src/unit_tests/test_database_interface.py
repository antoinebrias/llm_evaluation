import sys
sys.path.append('../src')

import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from database_interface import connect_db

class TestConnectDB(unittest.TestCase):
    @patch('sqlite3.connect')  # Mock sqlite3.connect
    def test_connect_db_success(self, mock_connect):
        # Arrange: set up a mock return value for sqlite3.connect
        mock_connection = MagicMock()  # Create a mock connection object
        mock_connect.return_value = mock_connection

        # Act: call the connect_db function
        db_path = "test.db"  # Path to your mock database
        result = connect_db(db_path)

        # Assert: check that sqlite3.connect was called with the correct path
        mock_connect.assert_called_once_with(db_path)
        
        # Assert: check that the returned result is the mocked connection
        self.assertEqual(result, mock_connection)

    @patch('sqlite3.connect')
    def test_connect_db_failure(self, mock_connect):
        # Arrange: simulate a failure, e.g., raise an exception when connecting to the DB
        mock_connect.side_effect = sqlite3.Error("Database connection failed")

        # Act & Assert: ensure that the function raises the expected exception
        db_path = "invalid.db"  # Path to an invalid database
        with self.assertRaises(sqlite3.Error):
            connect_db(db_path)


if __name__ == '__main__':
    unittest.main()
