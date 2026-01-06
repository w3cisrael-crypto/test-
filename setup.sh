#!/bin/bash
# Super Agent - סקריפט התקנה למתחילים
# הרץ סקריפט זה כדי להתקין את כל התלויות

echo "======================================"
echo "  Super Agent - התקנה אוטומטית"
echo "======================================"
echo ""

# בדיקת Python
echo "🔍 בודק אם Python מותקן..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "✓ נמצא Python 3"
    python3 --version
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "✓ נמצא Python"
    python --version
else
    echo "✗ Python לא מותקן!"
    echo "אנא התקן Python 3.9 ומעלה מ-https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "📦 יוצר סביבה וירטואלית..."
$PYTHON_CMD -m venv venv

# הפעלת הסביבה הוירטואלית
echo "🔄 מפעיל סביבה וירטואלית..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo "✓ סביבה וירטואלית הופעלה"
echo ""

# שדרוג pip
echo "⬆️  משדרג pip..."
pip install --upgrade pip

echo ""
echo "📥 מתקין תלויות..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "✅ ההתקנה הושלמה בהצלחה!"
echo "======================================"
echo ""
echo "📝 השלבים הבאים:"
echo "1. שים את קובץ service-account.json בתיקייה הזו"
echo "2. הרץ את המערכת:"
echo "   streamlit run app.py"
echo ""
echo "💡 לעזרה נוספת, ראה את DEPLOY.md"
echo ""
