"""
בדיקות למודול GSC Connector
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# הוסף את תיקיית הבסיס ל-PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.collectors.gsc_connector import GSCConnector, fetch_gsc_data


class TestGSCConnector:
    """בדיקות למחלקת GSCConnector"""

    def test_init(self):
        """בדיקת אתחול המחלקה"""
        connector = GSCConnector()
        assert connector.service is None
        assert connector.key_file is not None

    def test_init_with_custom_key(self):
        """בדיקת אתחול עם מפתח מותאם אישית"""
        custom_key = "custom_key.json"
        connector = GSCConnector(key_file=custom_key)
        assert connector.key_file == custom_key

    @patch('src.collectors.gsc_connector.ServiceAccountCredentials')
    @patch('src.collectors.gsc_connector.build')
    def test_connect_success(self, mock_build, mock_creds):
        """בדיקת חיבור מוצלח"""
        # הגדרת mocks
        mock_creds.from_json_keyfile_name.return_value = Mock()
        mock_build.return_value = Mock()

        connector = GSCConnector()
        result = connector.connect()

        assert result is True
        assert connector.service is not None

    @patch('src.collectors.gsc_connector.ServiceAccountCredentials')
    def test_connect_file_not_found(self, mock_creds):
        """בדיקת טיפול בקובץ חסר"""
        mock_creds.from_json_keyfile_name.side_effect = FileNotFoundError()

        connector = GSCConnector()
        result = connector.connect()

        assert result is False

    @patch('src.collectors.gsc_connector.ServiceAccountCredentials')
    @patch('src.collectors.gsc_connector.build')
    def test_fetch_data_success(self, mock_build, mock_creds):
        """בדיקת משיכת נתונים מוצלחת"""
        # הגדרת mocks
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # תוצאה מדומה מה-API
        mock_response = {
            'rows': [
                {
                    'keys': ['query1', 'https://example.com/page1'],
                    'clicks': 100,
                    'impressions': 1000,
                    'ctr': 0.1,
                    'position': 5.0
                },
                {
                    'keys': ['query2', 'https://example.com/page2'],
                    'clicks': 50,
                    'impressions': 500,
                    'ctr': 0.1,
                    'position': 8.0
                }
            ]
        }

        mock_service.searchanalytics().query().execute.return_value = mock_response

        connector = GSCConnector()
        connector.service = mock_service

        df = connector.fetch_data('https://example.com', '2024-01-01', '2024-01-31')

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'query' in df.columns
        assert 'page' in df.columns
        assert df['query'].iloc[0] == 'query1'

    @patch('src.collectors.gsc_connector.ServiceAccountCredentials')
    @patch('src.collectors.gsc_connector.build')
    def test_fetch_data_no_results(self, mock_build, mock_creds):
        """בדיקת משיכת נתונים ללא תוצאות"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # תוצאה ריקה
        mock_response = {}
        mock_service.searchanalytics().query().execute.return_value = mock_response

        connector = GSCConnector()
        connector.service = mock_service

        df = connector.fetch_data('https://example.com', '2024-01-01', '2024-01-31')

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_save_data_empty_dataframe(self, tmp_path):
        """בדיקת שמירת DataFrame ריק"""
        connector = GSCConnector()
        df = pd.DataFrame()

        result = connector.save_data(df)

        assert result is None


def test_fetch_gsc_data_helper_function():
    """בדיקת פונקציית העזר fetch_gsc_data"""
    with patch.object(GSCConnector, 'fetch_data') as mock_fetch:
        mock_fetch.return_value = pd.DataFrame({'test': [1, 2, 3]})

        result = fetch_gsc_data('https://example.com', '2024-01-01', '2024-01-31')

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
