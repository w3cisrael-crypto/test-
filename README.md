# Super Agent - מערכת תכנון תוכן אוטומטית

מערכת מתקדמת לתכנון תוכן מבוסס נתונים עבור סוכנויות SEO.

## 🚀 התחלה מהירה

**🆕 דרך חדשה ופשוטה - ללא הגדרת API!**
- 📁 **[איך להוריד CSV מ-Search Console](HOW_TO_EXPORT_GSC.md)** - מדריך 2 דקות
- 🌐 **[העלאה לאונליין (פשוטה)](DEPLOY.md)** - ללא Google Cloud או credentials!

**חדש? מתחיל בתכנות?**
- 📘 **[מדריך התחלה מהירה למתחילים](QUICKSTART.md)** - כל מה שצריך להתחיל
- 🔌 **[העלאה עם API (מתקדם)](DEPLOY.md#אפשרות-2-streamlit-cloud-עם-api-למתקדמים-)** - חיבור אוטומטי ל-GSC

**משתמש מתקדם?**
- המשך לקרוא למטה לפרטים טכניים מלאים

---

## 💡 שתי דרכים להשתמש במערכת

### 1. העלאת קובץ CSV (מומלץ למתחילים) 📁
- ✅ **פשוט** - ללא הגדרות טכניות
- ✅ **בטוח** - אין צורך ב-credentials
- ✅ **מהיר** - 2 דקות להוריד מ-GSC
- ⚠️ צריך להוריד קובץ חדש כל פעם

### 2. חיבור API (למתקדמים) 🔌
- ✅ **אוטומטי** - משוך נתונים ישירות מ-GSC
- ✅ **גמיש** - בחר טווח תאריכים דינמי
- ⚠️ דורש הגדרת Service Account
- ⚠️ דורש Google Cloud API

## סטטוס הפרויקט

**שלב נוכחי: שלב 4 - Dashboard** ✅

✅ מבנה הפרויקט הוקם
✅ חיבור ל-Google Search Console
✅ מנוע ניקוד והמלצות (שלב 2)
✅ מנוע תכנון חודשי (שלב 3)
✅ ממשק משתמש (שלב 4)

## תכונות מרכזיות

### שלב 1 - איסוף נתונים ✅
- **שתי שיטות קלט**:
  - 📁 **העלאת קובץ CSV** (פשוט, מומלץ למתחילים)
  - 🔌 **חיבור ל-Google Search Console API** (אוטומטי, מתקדם)
- **ניתוח נתונים**: Clicks, Impressions, CTR, Position לכל שאילתה
- **שמירת נתונים**: ייצוא לפורמט CSV/JSON

### שלב 2 - מנוע ניקוד והמלצות ✅
- **Opportunity Scoring**: ציון 0-100 לכל מילת מפתח על בסיס 3 רכיבים:
  - פוטנציאל טראפיק (40%)
  - מרחק נגיעה - מיקום (40%)
  - Quick Wins - שיפור CTR (20%)
- **ניקוי נתונים מתקדם**: סינון מותגים, נירמול, קטגוריזציה
- **המלצות אוטומטיות**: המלצת פעולה לכל הזדמנות
- **תובנות סטטיסטיות**: דוח מפורט עם מטריקות מרכזיות

### שלב 3 - תכנון תוכן חודשי ✅
- **Clustering**: קיבוץ אוטומטי של מילות מפתח דומות למניעת קניבליזציה
- **תכנון אסטרטגי**: בניית תוכנית חודשית עם איזון Pillar/Cluster (30/70)
- **3 אסטרטגיות תכנון**:
  - Balanced: איזון אופטימלי בין תוכן עומק לתוכן תומך
  - Pillar Focused: דגש על תוכן עומק (50/50)
  - Quick Wins: התמקדות בהזדמנויות מהירות
- **לוח זמנים אוטומטי**: הצעת תאריכי פרסום מותאמים
- **Content Briefs**: בריף מלא לכל מאמר (אורך, עומק, פעולות)

### שלב 4 - Dashboard אינטראקטיבי ✅
- **ממשק Streamlit מקצועי**: ניהול ויזואלי של כל התהליך
- **4 טאבים עיקריים**:
  - 📊 סקירה: מטריקות ראשיות וגרפים
  - 🎯 הזדמנויות: רשימה מפורטת עם המלצות
  - 🔗 קלאסטרים: ניתוח נושאים וקיבוצים
  - 📅 תוכנית: יצירת והצגת תוכנית תוכן
- **גרפים אינטראקטיביים**: Plotly charts להצגה ויזואלית
- **ייצוא קל**: הורדת תוכניות ובריפים ישירות מהממשק
- **Responsive Design**: עיצוב מותאם למסכים שונים

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

### אופציה 1: Dashboard (מומלץ) 🌟

הרצת הממשק הגרפי:

```bash
streamlit run app.py
```

הדפדפן ייפתח אוטומטית ב-`http://localhost:8501`

**תהליך העבודה ב-Dashboard:**
1. הזן כתובת אתר בסרגל הצד
2. בחר תקופת נתונים (ימים)
3. הוסף מילות מותג (אופציונלי)
4. הקלק "טען נתונים"
5. עבור בין הטאבים לניתוח
6. צור תוכנית תוכן מותאמת
7. הורד תוכנית ובריפים

### אופציה 2: CLI (שורת פקודה)

#### שימוש בסיסי - איסוף נתונים

```bash
# איסוף נתונים פשוט
python main.py --site https://example.com

# עם שמירה לקובץ
python main.py --site https://example.com --save

# טווח תאריכים מותאם
python main.py --site https://example.com --days 60
```

#### ניתוח והמלצות

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

#### תכנון תוכן חודשי

```bash
# תוכנית תוכן חודשית מלאה
python main.py --site https://example.com --analyze --plan

# תוכנית עם התאמות
python main.py --site https://example.com --analyze --plan \
  --num-articles 15 \      # 15 מאמרים לחודש
  --strategy pillar_focused \  # דגש על Pillar
  --posts-per-week 4 \     # 4 פוסטים בשבוע
  --save                   # שמור תוכנית ובריפים

# אסטרטגיית Quick Wins
python main.py --site https://example.com --analyze --plan \
  --strategy quick_wins \
  --num-articles 10
```

### אופציה 3: שימוש כספרייה

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

#### שלב 3 - תכנון תוכן

```python
from src.logic import KeywordClusterer, ContentPlanner, create_comprehensive_plan

# 1. קיבוץ מילות מפתח
clusterer = KeywordClusterer(language='hebrew')
df_clustered = clusterer.cluster_keywords(df_scored)

# 2. יצירת תוכנית מקיפה
plan_result = create_comprehensive_plan(
    df_clustered,
    num_articles=12,
    strategy='balanced',
    posts_per_week=3
)

# 3. גישה לתוכנית והבריפים
plan_df = plan_result['plan']
briefs = plan_result['briefs']
summary = plan_result['summary']

print(f"נוצרו {summary['total_articles']} מאמרים")
print(f"Pillar: {summary['pillar_articles']}, Cluster: {summary['cluster_articles']}")
```

## מבנה הפרויקט

```
seo_planner_agent/
├── app.py                       # 🌟 Dashboard (Streamlit)
├── main.py                      # CLI - שורת פקודה
├── config/
│   ├── settings.py              # הגדרות כלליות
│   └── clients_config.yaml      # הגדרות לקוחות
├── data/
│   ├── raw/                     # נתונים גולמיים
│   └── processed/               # נתונים מעובדים + תוכניות
├── src/
│   ├── collectors/              # מודולי איסוף נתונים
│   │   └── gsc_connector.py     # חיבור ל-GSC (שלב 1) ✅
│   ├── logic/                   # לוגיקה עסקית
│   │   ├── scoring.py           # מנוע ניקוד (שלב 2) ✅
│   │   ├── clustering.py        # קיבוץ מילות מפתח (שלב 3) ✅
│   │   └── planner.py           # תכנון תוכן (שלב 3) ✅
│   └── utils/
│       └── data_cleaning.py     # ניקוי נתונים (שלב 2) ✅
├── tests/                       # בדיקות אוטומטיות
└── requirements.txt             # תלויות
```

## תכונות מיוחדות

### Dashboard (app.py)
- **ממשק אינטראקטיבי** עם Streamlit
- **גרפים דינמיים** עם Plotly
- **ניווט קל** בין טאבים
- **ייצוא מהיר** של תוצאות
- **עיצוב מקצועי** עם CSS מותאם

### CLI (main.py)
- **גמישות מקסימלית** עם פרמטרים רבים
- **אוטומציה** מלאה לסקריפטים
- **פלט עשיר** עם אמוג'ים ומבנה ברור

### ספרייה (Python API)
- **שילוב קל** בפרויקטים קיימים
- **שליטה מלאה** על כל שלב
- **התאמה אישית** של אלגוריתמים

## תרומה

הפרויקט נמצא בפיתוח פעיל. לשאלות או בעיות, פתח Issue ב-GitHub.

## רישיון

© 2024 - מערכת תכנון תוכן אוטומטית
