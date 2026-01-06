"""
Super Agent - מערכת תכנון תוכן
נקודת כניסה ראשית למערכת

שלב 1: בדיקת חיבור ל-GSC ומשיכת נתונים בסיסית
"""
import argparse
from datetime import datetime, timedelta
from src.collectors import GSCConnector


def main():
    """
    פונקציה ראשית - שלב 1
    """
    print("=" * 60)
    print("Super Agent - מערכת תכנון תוכן אוטומטית")
    print("=" * 60)
    print("שלב 1: איסוף נתונים מ-Google Search Console")
    print("=" * 60)
    print()

    # ארגומנטים מהשורת הפקודה
    parser = argparse.ArgumentParser(
        description='משיכת נתונים מ-Google Search Console'
    )
    parser.add_argument(
        '--site',
        type=str,
        help='כתובת האתר (לדוגמה: https://example.com)',
        required=False
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='מספר ימים אחורה (ברירת מחדל: 30)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='שמירת הנתונים לקובץ CSV'
    )

    args = parser.parse_args()

    # אם לא סופק אתר, בקש מהמשתמש
    if not args.site:
        print("אנא הזן את כתובת האתר שלך:")
        print("דוגמאות:")
        print("  - https://example.com")
        print("  - sc-domain:example.com")
        print()
        site_url = input("כתובת האתר: ").strip()

        if not site_url:
            print("✗ לא הוזנה כתובת אתר. יציאה...")
            return
    else:
        site_url = args.site

    # חישוב טווח תאריכים
    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=args.days + 3)).strftime('%Y-%m-%d')

    print(f"\nמשיכת נתונים עבור: {site_url}")
    print(f"טווח תאריכים: {start_date} עד {end_date}")
    print()

    # יצירת המחבר
    connector = GSCConnector()

    # חיבור ל-API
    if not connector.connect():
        print("\n✗ נכשל בחיבור ל-Google Search Console")
        print("\nוודא ש:")
        print("  1. קובץ service-account.json קיים בתיקיית הפרויקט")
        print("  2. ה-Service Account הוסף כמשתמש ב-Search Console")
        print("  3. Search Console API מופעל בפרויקט ב-Google Cloud")
        return

    # משיכת נתונים
    df = connector.fetch_data(site_url, start_date, end_date)

    if df.empty:
        print("\n✗ לא נמשכו נתונים. בדוק את כתובת האתר והתאריכים.")
        return

    # הצגת סיכום
    print("\n" + "=" * 60)
    print("סיכום הנתונים")
    print("=" * 60)
    print(f"סה\"כ שאילתות: {len(df)}")
    print(f"סה\"כ קליקים: {df['clicks'].sum():,.0f}")
    print(f"סה\"כ חשיפות: {df['impressions'].sum():,.0f}")
    print(f"CTR ממוצע: {df['ctr'].mean():.2%}")
    print(f"מיקום ממוצע: {df['position'].mean():.1f}")

    # הצגת 10 השאילתות המובילות
    print("\n" + "=" * 60)
    print("10 השאילתות המובילות (לפי קליקים)")
    print("=" * 60)
    top_queries = df.nlargest(10, 'clicks')
    for idx, row in top_queries.iterrows():
        print(f"\n{row['query']}")
        print(f"  קליקים: {row['clicks']:,.0f} | חשיפות: {row['impressions']:,.0f} | "
              f"CTR: {row['ctr']:.2%} | מיקום: {row['position']:.1f}")

    # שמירה לקובץ
    if args.save:
        print("\n" + "=" * 60)
        filepath = connector.save_data(df)
        if filepath:
            print(f"✓ הנתונים נשמרו בהצלחה: {filepath}")

    print("\n" + "=" * 60)
    print("✓ השלמה בהצלחה!")
    print("=" * 60)


if __name__ == "__main__":
    main()
