# מדריך העלאה לאונליין - למתחילים 🚀

מדריך פשוט ומפורט להעלאת מערכת Super Agent לאינטרנט בחינם!

---

## ⚡ שיטה קלה ומהירה (ללא API!) - חדש! 🆕

**הדרך הכי פשוטה להתחיל:**

1. **העלה את הקוד ל-Streamlit Cloud** (ראה למטה)
2. **הורד CSV מ-Search Console** (ראה [מדריך פשוט](HOW_TO_EXPORT_GSC.md))
3. **העלה את הקובץ באפליקציה** - זהו!

**יתרונות:**
- ✅ **אין צורך ב-Google Cloud** או Service Account
- ✅ **אין צורך ב-Secrets** או credentials
- ✅ **פשוט להעלות ל-Streamlit Cloud** - רק הקוד
- ✅ **בטוח יותר** - אין גישה ל-API
- ✅ **מהיר** - 5 דקות סה"כ

**חסרון יחיד:**
- ⚠️ צריך להוריד קובץ חדש מ-GSC כל פעם (לא אוטומטי)

אם השיטה הזו מתאימה לך, דלג ישר ל**"אפשרות 1: Streamlit Cloud - העלאה פשוטה"** למטה.

---

## אפשרות 1: Streamlit Cloud - העלאה פשוטה (ללא API) ⭐

השיטה הזו **לא דורשת** הגדרת Google Cloud או Service Account!

### שלב 1: העלה את הקוד ל-GitHub

1. **אם יש לך חשבון GitHub**:
   ```bash
   git push origin claude/content-planning-stage-1-UtjTj
   ```

2. **אם אין לך חשבון GitHub**:
   - גש ל-https://github.com
   - לחץ "Sign up"
   - מלא פרטים ואמת מייל
   - צור repository חדש
   - העלה את הקוד

### שלב 2: פריסה ל-Streamlit Cloud

1. **גש ל-Streamlit Cloud**:
   - https://share.streamlit.io

2. **התחבר עם GitHub**:
   - לחץ "Sign up"
   - בחר "Continue with GitHub"
   - אשר הרשאות

3. **צור אפליקציה**:
   - לחץ "New app"
   - בחר את ה-repository שלך
   - בחר branch: `claude/content-planning-stage-1-UtjTj`
   - Main file: `app.py`
   - לחץ "Deploy"

4. **המתן להעלאה** (1-3 דקות)

5. **זהו!** תקבל קישור כמו: `https://your-app.streamlit.app`

### שלב 3: שימוש באפליקציה

1. **פתח את הקישור** שקיבלת
2. **בסרגל הצד**, בחר **"📁 העלה קובץ CSV (פשוט)"**
3. **הורד CSV מ-Search Console** ([מדריך מפורט](HOW_TO_EXPORT_GSC.md))
4. **העלה את הקובץ**
5. **לחץ "טען נתונים"** - זהו!

**זה הכל! אפליקציה פועלת באינטרנט ללא הגדרות מורכבות!** 🎉

---

## אפשרות 2: Streamlit Cloud עם API (למתקדמים) 🔌

אם אתה רוצה שהמערכת תמשוך נתונים **אוטומטית** מ-GSC (ללא הורדה ידנית), תצטרך להגדיר API.

Streamlit Cloud הוא שירות חינמי שמאפשר לך להריץ את המערכת באינטרנט תוך דקות ספורות.

### שלב 1: הכנת חשבון GitHub

1. **צור חשבון GitHub** (אם אין לך):
   - גש ל-https://github.com
   - לחץ על "Sign up"
   - מלא פרטים ואמת את המייל

2. **העלה את הפרויקט ל-GitHub**:
   ```bash
   # הפרויקט כבר ב-Git, רק צריך לדחוף אותו
   git push origin claude/content-planning-stage-1-UtjTj
   ```

### שלב 2: הכנת Google Service Account

1. **גש ל-Google Cloud Console**:
   - https://console.cloud.google.com

2. **צור פרויקט חדש**:
   - לחץ על "Select a project" למעלה
   - לחץ "NEW PROJECT"
   - תן שם לפרויקט (למשל: "seo-planner")
   - לחץ "Create"

3. **הפעל את Search Console API**:
   - בתפריט השמאלי: "APIs & Services" > "Enable APIs and Services"
   - חפש "Google Search Console API"
   - לחץ "Enable"

4. **צור Service Account**:
   - "APIs & Services" > "Credentials"
   - "Create Credentials" > "Service Account"
   - תן שם (למשל: "seo-planner-bot")
   - לחץ "Create and Continue"
   - בחר תפקיד: "Owner" (לבינתיים)
   - לחץ "Done"

5. **הורד את קובץ ה-JSON**:
   - לחץ על Service Account שיצרת
   - טאב "Keys" > "Add Key" > "Create new key"
   - בחר "JSON"
   - הקובץ יורד אוטומטית למחשב שלך

6. **העתק את תוכן הקובץ**:
   - פתח את הקובץ שהורדת בעורך טקסט
   - העתק את **כל התוכן** (Ctrl+A, Ctrl+C)
   - **שמור אותו בצד - נצטרך אותו בשלב הבא!**

7. **הוסף הרשאות ב-Search Console**:
   - גש ל-https://search.google.com/search-console
   - בחר את האתר שלך
   - Settings (גלגל השיניים) > "Users and permissions"
   - "Add user"
   - הדבק את המייל של Service Account (נראה כמו: `xxx@xxx.iam.gserviceaccount.com`)
   - בחר "Full" permissions
   - לחץ "Add"

### שלב 3: יצירת חשבון Streamlit Cloud

1. **גש ל-Streamlit Cloud**:
   - https://share.streamlit.io

2. **התחבר עם GitHub**:
   - לחץ "Sign up"
   - בחר "Continue with GitHub"
   - אשר הרשאות

### שלב 4: פריסת האפליקציה

1. **צור אפליקציה חדשה**:
   - לחץ "New app" בדף הראשי

2. **מלא פרטים**:
   - **Repository**: בחר את ה-repository שלך
   - **Branch**: בחר `claude/content-planning-stage-1-UtjTj`
   - **Main file path**: `app.py`
   - לחץ "Deploy"

3. **הגדר Secrets** (חשוב מאוד!):
   - בזמן שהאפליקציה נטענת, לחץ על "Advanced settings"
   - או: אחרי הפריסה, לחץ על תפריט המבורגר (⋮) > "Settings" > "Secrets"
   - הדבק את זה (החלף את `YOUR_SERVICE_ACCOUNT_JSON` בתוכן הקובץ שהורדת):

   ```toml
   [gsc]
   service_account_info = '''
   YOUR_SERVICE_ACCOUNT_JSON
   '''
   ```

   **דוגמה איך זה צריך להראות**:
   ```toml
   [gsc]
   service_account_info = '''
   {
     "type": "service_account",
     "project_id": "your-project-123",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...",
     "client_email": "xxx@xxx.iam.gserviceaccount.com",
     "client_id": "123...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     ...
   }
   '''
   ```

4. **שמור והמתן**:
   - לחץ "Save"
   - המערכת תתחיל לטעון (1-3 דקות)
   - ברגע שמוכן, תקבל קישור כמו: `https://your-app-name.streamlit.app`

### שלב 5: שימוש במערכת

1. **גש לקישור שקיבלת**
2. **הזן פרטים בסרגל הצד**:
   - כתובת אתר (בדיוק כמו ב-Search Console, למשל: `https://example.com`)
   - תקופת נתונים (המלצה: 90 ימים)
   - מילות מותג (אופציונלי)
3. **לחץ "טען נתונים"**
4. **עבור בין הטאבים**:
   - 📊 סקירה - מבט על
   - 🎯 הזדמנויות - רשימת המלצות
   - 🔗 קלאסטרים - קיבוצי תוכן
   - 📅 תוכנית - יצירת תוכנית תוכן

---

## אפשרות 2: הרצה מקומית על המחשב שלך 💻

אם אתה מעדיף להריץ על המחשב שלך (ללא אינטרנט):

### דרישות מוקדמות

1. **התקן Python** (גרסה 3.9 ומעלה):
   - Windows: הורד מ-https://www.python.org/downloads/
   - Mac: `brew install python3`
   - Linux: `sudo apt install python3 python3-pip`

2. **ודא שPython מותקן**:
   ```bash
   python --version
   # או
   python3 --version
   ```

### התקנה והפעלה

1. **פתח Terminal/Command Prompt** בתיקיית הפרויקט

2. **צור סביבה וירטואלית**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **התקן תלויות**:
   ```bash
   pip install -r requirements.txt
   ```

4. **שים את קובץ Service Account**:
   - שמור את קובץ ה-JSON שהורדת בשם `service-account.json`
   - שים אותו **בתיקייה הראשית של הפרויקט** (ליד `app.py`)

5. **הרץ את המערכת**:
   ```bash
   streamlit run app.py
   ```

6. **פתח בדפדפן**:
   - הדפדפן יפתח אוטומטית ב-`http://localhost:8501`
   - אם לא, פתח את הקישור הזה ידנית

---

## פתרון בעיות 🔧

### שגיאה: "No module named 'streamlit'"
**פתרון**:
```bash
pip install streamlit
```

### שגיאה: "Service account credentials not found"
**פתרון**:
- ודא שקובץ `service-account.json` נמצא בתיקייה הנכונה
- או: הגדר Secrets ב-Streamlit Cloud כמו בשלב 4.3

### שגיאה: "Permission denied" מ-Google
**פתרון**:
- ודא שהוספת את Service Account למשתמשים ב-Search Console (שלב 2.7)
- ודא שהמייל של Service Account זהה למה שב-JSON

### האפליקציה לא נטענת ב-Streamlit Cloud
**פתרון**:
- בדוק את ה-Logs בממשק Streamlit Cloud
- ודא ש-`requirements.txt` מעודכן
- ודא שה-Secrets מוגדרים נכון

### שאלות ובעיות נוספות
פתח Issue ב-GitHub או בדוק את הלוגים בממשק.

---

## טיפים לשימוש מיטבי 💡

1. **תקופת נתונים**:
   - למחקר ראשוני: 90 ימים
   - לניטור שוטף: 30 ימים
   - לטרנדים: 180 ימים

2. **מילות מותג**:
   - הוסף את שם החברה
   - הוסף וריאציות (למשל: "אקמי", "acme", "ACME")
   - זה מסנן מילות מפתח שלא רלוונטיות

3. **אסטרטגיות תכנון**:
   - **Balanced**: מאוזן - טוב לרוב המקרים
   - **Pillar Focused**: למותגים חדשים שרוצים לבסס authority
   - **Quick Wins**: לתוצאות מהירות, טוב לתחילת עבודה

4. **ייצוא נתונים**:
   - שמור את התוכניות כ-JSON או CSV
   - הורד את הבריפים למאמרים
   - שתף עם צוות התוכן

---

## אבטחה וחשאיות 🔒

**חשוב מאוד**:
- ⚠️ **לעולם אל תעלה את קובץ `service-account.json` ל-GitHub**
- ⚠️ הקובץ כבר מוגדר ב-`.gitignore` אבל בדוק פעמיים
- ⚠️ ב-Streamlit Cloud, השתמש ב-Secrets בלבד, לא בקבצים
- ⚠️ אל תשתף את ה-Secrets או ה-JSON עם אף אחד

---

## סיכום מהיר ⚡

**רוצה להעלות לאונליין? (מומלץ)**
1. צור חשבון GitHub ודחוף את הקוד
2. צור Service Account ב-Google Cloud
3. הוסף את Service Account ל-Search Console
4. צור חשבון ב-Streamlit Cloud
5. פרוס את האפליקציה והגדר Secrets
6. זהו! המערכת זמינה באינטרנט

**רוצה להריץ מקומית?**
1. התקן Python 3.9+
2. `pip install -r requirements.txt`
3. שים `service-account.json` בתיקייה
4. `streamlit run app.py`
5. זהו! המערכת רצה על `localhost:8501`

---

**בהצלחה! 🎉**

אם יש שאלות, פתח Issue ב-GitHub.
