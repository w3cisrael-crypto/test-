@echo off
REM Super Agent - סקריפט התקנה למתחילים (Windows)
REM הרץ סקריפט זה כדי להתקין את כל התלויות

echo ======================================
echo   Super Agent - התקנה אוטומטית
echo ======================================
echo.

REM בדיקת Python
echo בודק אם Python מותקן...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python לא מותקן!
    echo אנא התקן Python 3.9 ומעלה מ-https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo נמצא Python
echo.

echo יוצר סביבה וירטואלית...
python -m venv venv

echo מפעיל סביבה וירטואלית...
call venv\Scripts\activate.bat

echo סביבה וירטואלית הופעלה
echo.

echo משדרג pip...
python -m pip install --upgrade pip

echo.
echo מתקין תלויות...
pip install -r requirements.txt

echo.
echo ======================================
echo ההתקנה הושלמה בהצלחה!
echo ======================================
echo.
echo השלבים הבאים:
echo 1. שים את קובץ service-account.json בתיקייה הזו
echo 2. הרץ את המערכת:
echo    streamlit run app.py
echo.
echo לעזרה נוספת, ראה את DEPLOY.md
echo.
pause
