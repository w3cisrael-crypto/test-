"""
Google Search Console Data Collector
מודול לאיסוף נתוני מילות מפתח מ-Google Search Console
"""
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import sys
from pathlib import Path

# הוסף את תיקיית הבסיס ל-PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import GSC_SCOPES, GSC_KEY_FILE, DEFAULT_ROW_LIMIT


class GSCConnector:
    """
    מחלקה לניהול החיבור והנתונים מ-Google Search Console
    """

    def __init__(self, key_file=None):
        """
        אתחול החיבור ל-GSC

        Args:
            key_file (str): נתיב לקובץ ה-service account JSON
        """
        self.key_file = key_file or GSC_KEY_FILE
        self.service = None

    def connect(self):
        """
        יצירת חיבור ל-GSC API
        """
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.key_file,
                GSC_SCOPES
            )
            self.service = build('webmasters', 'v3', credentials=creds)
            print("✓ חיבור ל-Google Search Console הושלם בהצלחה")
            return True
        except FileNotFoundError:
            print(f"✗ שגיאה: קובץ ה-credentials לא נמצא: {self.key_file}")
            print("  אנא וודא שקובץ service-account.json קיים בתיקיית הפרויקט")
            return False
        except Exception as e:
            print(f"✗ שגיאה בחיבור ל-GSC: {str(e)}")
            return False

    def fetch_data(self, site_url, start_date=None, end_date=None, row_limit=None):
        """
        משיכת נתוני מילות מפתח מ-GSC

        Args:
            site_url (str): כתובת האתר (לדוגמה: 'https://example.com' או 'sc-domain:example.com')
            start_date (str): תאריך התחלה בפורמט 'YYYY-MM-DD'
            end_date (str): תאריך סיום בפורמט 'YYYY-MM-DD'
            row_limit (int): מספר השורות המקסימלי להחזרה

        Returns:
            pandas.DataFrame: טבלה עם הנתונים או DataFrame ריק במקרה של שגיאה
        """
        if not self.service:
            if not self.connect():
                return pd.DataFrame()

        # ברירת מחדל: 30 יום אחרונים
        if not end_date:
            end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=33)).strftime('%Y-%m-%d')

        row_limit = row_limit or DEFAULT_ROW_LIMIT

        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query', 'page'],
            'rowLimit': row_limit
        }

        try:
            print(f"מושך נתונים עבור {site_url} מ-{start_date} עד {end_date}...")
            response = self.service.searchanalytics().query(
                siteUrl=site_url,
                body=request
            ).execute()

            if 'rows' not in response:
                print("✗ לא נמצאו נתונים לתאריכים המבוקשים")
                return pd.DataFrame()

            # המרת התוצאות ל-DataFrame
            df = pd.DataFrame(response['rows'])

            # פירוק הנתונים לטורים נוחים
            df['query'] = df['keys'].apply(lambda x: x[0])
            df['page'] = df['keys'].apply(lambda x: x[1] if len(x) > 1 else '')
            df = df.drop(columns=['keys'])

            print(f"✓ נמשכו {len(df)} שורות בהצלחה")
            return df

        except Exception as e:
            print(f"✗ שגיאה במשיכת נתונים: {str(e)}")
            return pd.DataFrame()

    def save_data(self, df, filename=None):
        """
        שמירת הנתונים לקובץ CSV

        Args:
            df (pandas.DataFrame): הנתונים לשמירה
            filename (str): שם הקובץ (אופציונלי)

        Returns:
            str: נתיב הקובץ ששמור או None במקרה של שגיאה
        """
        if df.empty:
            print("✗ אין נתונים לשמירה")
            return None

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gsc_data_{timestamp}.csv"

        # ודא שהתיקייה קיימת
        from config.settings import RAW_DATA_DIR
        filepath = RAW_DATA_DIR / filename

        try:
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✓ הנתונים נשמרו בהצלחה: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"✗ שגיאה בשמירת הנתונים: {str(e)}")
            return None


def fetch_gsc_data(site_url, start_date, end_date, key_file=None):
    """
    פונקציית עזר לשימוש מהיר (תואמת את הדוגמה בתוכנית)

    Args:
        site_url (str): כתובת האתר
        start_date (str): תאריך התחלה
        end_date (str): תאריך סיום
        key_file (str): נתיב לקובץ credentials (אופציונלי)

    Returns:
        pandas.DataFrame: טבלה עם הנתונים
    """
    connector = GSCConnector(key_file)
    return connector.fetch_data(site_url, start_date, end_date)


if __name__ == "__main__":
    """
    בדיקה מהירה של המודול
    """
    print("=== בדיקת מודול GSC Connector ===\n")

    # דוגמה לשימוש
    test_url = "https://example.com"  # החלף בכתובת האתר שלך

    connector = GSCConnector()

    # נסיון חיבור
    if connector.connect():
        # משיכת נתונים מ-30 הימים האחרונים
        df = connector.fetch_data(test_url)

        if not df.empty:
            print("\n=== תצוגה מקדימה של הנתונים ===")
            print(df.head())
            print(f"\nסה\"כ שורות: {len(df)}")
            print(f"טורים: {list(df.columns)}")

            # שמירה לקובץ
            connector.save_data(df)
    else:
        print("\nלא ניתן להתחבר ל-GSC. אנא בדוק את קובץ ה-credentials.")
