# מדריך התחלה מהירה - שלב 1

מדריך זה יעזור לך להפעיל את המערכת תוך מספר דקות.

## שלב 1: הכנת הסביבה

```bash
# צור סביבה וירטואלית
python -m venv venv

# הפעל את הסביבה
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate  # Windows

# התקן תלויות
pip install -r requirements.txt
```

## שלב 2: הגדרת Google Search Console

### 2.1 צור Service Account

1. גש ל-[Google Cloud Console](https://console.cloud.google.com/)
2. צור פרויקט חדש (או בחר קיים)
3. הפעל את **Search Console API**:
   - APIs & Services → Library
   - חפש "Google Search Console API"
   - לחץ Enable

### 2.2 צור Credentials

1. APIs & Services → Credentials
2. Create Credentials → Service Account
3. מלא שם (לדוגמה: "seo-planner")
4. תפקיד: Owner (או Viewer אם אתה רוצה רק קריאה)
5. Done

### 2.3 הורד את מפתח ה-JSON

1. לחץ על ה-Service Account שיצרת
2. Keys → Add Key → Create new key
3. בחר JSON
4. הקובץ יורד אוטומטית
5. **שנה שם הקובץ ל-`service-account.json`**
6. העתק אותו לתיקיית הפרויקט (השורש)

### 2.4 הוסף הרשאות ב-Search Console

1. גש ל-[Search Console](https://search.google.com/search-console)
2. בחר את האתר שלך
3. Settings (בסרגל הצד) → Users and permissions
4. Add user
5. הדבק את כתובת ה-email של ה-Service Account (מופיעה ב-Google Cloud)
6. בחר הרשאה: Owner או Full

## שלב 3: הרצה ראשונה

### אופציה 1: ריצה אינטראקטיבית

```bash
python main.py
```

המערכת תבקש ממך להזין כתובת אתר:

```
אנא הזן את כתובת האתר שלך:
דוגמאות:
  - https://example.com
  - sc-domain:example.com

כתובת האתר: https://mywebsite.com
```

### אופציה 2: ריצה עם פרמטרים

```bash
# דוגמה בסיסית
python main.py --site https://example.com

# עם שמירה לקובץ
python main.py --site https://example.com --save

# עם טווח תאריכים מותאם
python main.py --site https://example.com --days 60 --save
```

### אופציה 3: שימוש כמודול

צור קובץ Python חדש:

```python
from src.collectors import GSCConnector

# צור מחבר
connector = GSCConnector()

# התחבר
connector.connect()

# משוך נתונים
df = connector.fetch_data(
    site_url="https://example.com",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# הצג תוצאות
print(df.head())

# שמור
connector.save_data(df, "my_analysis.csv")
```

## שגיאות נפוצות ופתרונות

### ❌ "קובץ ה-credentials לא נמצא"

**פתרון:**
- ודא שקובץ `service-account.json` נמצא בתיקיית הבסיס של הפרויקט
- בדוק שהשם מדויק (כולל אותיות קטנות)

### ❌ "לא נמצאו נתונים"

**פתרון:**
- ודא שהוספת את ה-Service Account כמשתמש ב-Search Console
- בדוק שהאתר מאומת ב-Search Console
- ודא שיש נתונים בטווח התאריכים שבחרת

### ❌ "API not enabled"

**פתרון:**
- גש ל-Google Cloud Console
- ודא שה-Search Console API מופעל
- המתן כמה דקות לאחר ההפעלה

### ❌ "Insufficient permissions"

**פתרון:**
- ודא שה-Service Account הוסף ב-Search Console עם הרשאות מתאימות
- המתן כמה דקות לאחר הוספת המשתמש

## תוצאה מוצפת

לאחר הרצה מוצלחת, תראה:

```
============================================================
Super Agent - מערכת תכנון תוכן אוטומטית
============================================================
שלב 1: איסוף נתונים מ-Google Search Console
============================================================

✓ חיבור ל-Google Search Console הושלם בהצלחה
מושך נתונים עבור https://example.com מ-2023-12-01 עד 2024-01-01...
✓ נמשכו 1523 שורות בהצלחה

============================================================
סיכום הנתונים
============================================================
סה"כ שאילתות: 1523
סה"כ קליקים: 4,523
סה"כ חשיפות: 125,670
CTR ממוצע: 3.60%
מיקום ממוצע: 12.3

============================================================
10 השאילתות המובילות (לפי קליקים)
============================================================

מדריך SEO למתחילים
  קליקים: 342 | חשיפות: 5,230 | CTR: 6.54% | מיקום: 4.2

...
```

## מה הלאה?

✅ **שלב 1 הושלם!** - יש לך עכשיו מערכת פעילה למשיכת נתונים מ-GSC

הצעדים הבאים:
- **שלב 2**: הוספת מנוע ניקוד (Scoring Engine) לזיהוי הזדמנויות
- **שלב 3**: בניית מנוע תכנון חודשי
- **שלב 4**: יצירת ממשק משתמש עם Streamlit

## עזרה נוספת

- בדוק את `README.md` למידע מפורט יותר
- קרא את ההערות בקוד ב-`src/collectors/gsc_connector.py`
- הרץ בדיקות: `pytest tests/`
