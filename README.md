# Super Agent - מערכת תכנון תוכן אוטומטית

מערכת מתקדמת לתכנון תוכן מבוסס נתונים עבור סוכנויות SEO.

## סטטוס הפרויקט

**שלב נוכחי: שלב 2 - מנוע ניקוד והמלצות** ✅

✅ מבנה הפרויקט הוקם
✅ חיבור ל-Google Search Console
✅ מנוע ניקוד והמלצות (שלב 2)
⏳ מנוע תכנון חודשי (שלב 3)
⏳ ממשק משתמש (שלב 4)

## תכונות מרכזיות

### שלב 1 - איסוף נתונים ✅
- **חיבור ל-Google Search Console API**: משיכת נתוני מילות מפתח אוטומטית
- **ניתוח נתונים**: Clicks, Impressions, CTR, Position לכל שאילתה
- **שמירת נתונים**: ייצוא לפורמט CSV

### שלב 2 - מנוע ניקוד והמלצות ✅
- **Opportunity Scoring**: ציון 0-100 לכל מילת מפתח על בסיס 3 רכיבים:
  - פוטנציאל טראפיק (40%)
  - מרחק נגיעה - מיקום (40%)
  - Quick Wins - שיפור CTR (20%)
- **ניקוי נתונים מתקדם**: סינון מותגים, נירמול, קטגוריזציה
- **המלצות אוטומטיות**: המלצת פעולה לכל הזדמנות
- **תובנות סטטיסטיות**: דוח מפורט עם מטריקות מרכזיות

## התקנה

### דרישות מקדימות

- Python 3.9 ומעלה
- חשבון Google Cloud עם הרשאות ל-Search Console API
- קובץ Service Account (JSON)

### שלבי התקנה

1. **שכפול הפרויקט**
```bash
git clone <repository-url>
cd test-
```

2. **יצירת סביבה וירטואלית**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate  # Windows
```

3. **התקנת תלויות**
```bash
pip install -r requirements.txt
```

4. **הגדרת Credentials**
   - השג קובץ Service Account מ-Google Cloud Console
   - שמור אותו בתור `service-account.json` בתיקיית הפרויקט
   - **חשוב**: קובץ זה כבר מוגדר ב-.gitignore ולא יועלה ל-Git

## שימוש

### שימוש בסיסי - איסוף נתונים (שלב 1)

```bash
# איסוף נתונים פשוט
python main.py --site https://example.com

# עם שמירה לקובץ
python main.py --site https://example.com --save

# טווח תאריכים מותאם
python main.py --site https://example.com --days 60
```

### שימוש מתקדם - ניתוח והמלצות (שלב 2)

```bash
# ניתוח מלא עם המלצות
python main.py --site https://example.com --analyze

# עם סינון מילות מותג
python main.py --site https://example.com --analyze \
  --brand "שם החברה" "המותג"

# התאמת תוצאות
python main.py --site https://example.com --analyze \
  --top 20 \           # הצג 20 הזדמנויות
  --min-score 60 \     # ציון מינימלי
  --save              # שמור לקובץ
```

### שימוש כספרייה

#### שלב 1 - איסוף נתונים

```python
from src.collectors import GSCConnector

# יצירת מחבר
connector = GSCConnector()
connector.connect()

# משיכת נתונים
df = connector.fetch_data(
    site_url="https://example.com",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# שמירת נתונים
connector.save_data(df, "my_data.csv")
```

#### שלב 2 - ניקוד והמלצות

```python
from src.collectors import GSCConnector
from src.logic import OpportunityScorer, rank_opportunities
from src.utils import DataCleaner

# 1. משיכת נתונים
connector = GSCConnector()
connector.connect()
df = connector.fetch_data('https://example.com', '2024-01-01', '2024-01-31')

# 2. ניקוי נתונים
cleaner = DataCleaner(brand_keywords=['שם המותג'])
df_clean = cleaner.clean_pipeline(df)

# 3. חישוב ציונים
scorer = OpportunityScorer()
df_scored = scorer.score_dataframe(df_clean)

# 4. דירוג והצגה
top_opportunities = rank_opportunities(df_scored, top_n=10, min_score=70)
print(top_opportunities[['query', 'opportunity_score', 'position']])
```

## מבנה הפרויקט

```
seo_planner_agent/
├── config/
│   ├── settings.py              # הגדרות כלליות
│   └── clients_config.yaml      # הגדרות לקוחות
├── data/
│   ├── raw/                     # נתונים גולמיים
│   └── processed/               # נתונים מעובדים
├── src/
│   ├── collectors/              # מודולי איסוף נתונים
│   │   └── gsc_connector.py     # חיבור ל-GSC (שלב 1) ✅
│   ├── logic/                   # לוגיקה עסקית (שלב 2-3)
│   └── utils/                   # כלי עזר
├── tests/                       # בדיקות
├── main.py                      # נקודת כניסה
└── requirements.txt             # תלויות
```

## הגדרת Google Search Console API

1. **צור פרויקט ב-Google Cloud Console**
   - גש ל-[Google Cloud Console](https://console.cloud.google.com/)
   - צור פרויקט חדש

2. **הפעל את Search Console API**
   - בתפריט, עבור ל-"APIs & Services" > "Library"
   - חפש "Google Search Console API"
   - לחץ "Enable"

3. **צור Service Account**
   - עבור ל-"APIs & Services" > "Credentials"
   - לחץ "Create Credentials" > "Service Account"
   - מלא את הפרטים והורד את קובץ ה-JSON

4. **הוסף הרשאות ב-Search Console**
   - גש ל-[Search Console](https://search.google.com/search-console)
   - בחר את האתר שלך
   - Settings > Users and permissions
   - הוסף את כתובת ה-email של ה-Service Account

## טיפים לשימוש

### מניעת שימוש יתר ב-API
- השתמש ב-Caching: שמור נתונים מקומית
- הגדר טווחי תאריכים סבירים
- הימנע מריצות מרובות על אותם תאריכים

### אבטחה
- **לעולם אל תעלה את `service-account.json` ל-Git**
- שמור מפתחות API במשתני סביבה
- השתמש ב-`.env` לפיתוח מקומי

## שלבים הבאים

- [ ] **שלב 2**: מנוע ניקוד והמלצות
- [ ] **שלב 3**: מנוע תכנון חודשי עם Clustering
- [ ] **שלב 4**: Dashboard עם Streamlit
- [ ] **שלב 5**: ייצוא ושיתוף תוכניות

## תרומה

הפרויקט נמצא בפיתוח פעיל. לשאלות או בעיות, פתח Issue ב-GitHub.

## רישיון

© 2024 - מערכת תכנון תוכן אוטומטית
