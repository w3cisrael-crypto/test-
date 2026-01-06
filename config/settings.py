"""
הגדרות כלליות למערכת תכנון התוכן
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Google Search Console settings
GSC_SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
GSC_KEY_FILE = os.getenv('GSC_KEY_FILE', 'service-account.json')

# Data collection settings
DEFAULT_ROW_LIMIT = 5000
DEFAULT_DATE_RANGE_DAYS = 30

# Ensure data directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
