"""
Data Cleaning Utilities
כלי עזר לניקוי ועיבוד נתוני GSC
"""
import pandas as pd
import re
from typing import List, Optional, Set


class DataCleaner:
    """
    מחלקה לניקוי ועיבוד נתוני מילות מפתח
    """

    # מילים נפוצות לסינון (Stop words)
    HEBREW_STOPWORDS = {
        'של', 'את', 'עם', 'על', 'אל', 'מה', 'זה', 'זאת',
        'כל', 'או', 'אבל', 'גם', 'רק', 'עוד', 'כי', 'אם',
        'יש', 'היה', 'הוא', 'היא', 'אני', 'אתה'
    }

    def __init__(self, brand_keywords: Optional[List[str]] = None):
        """
        אתחול המנקה

        Args:
            brand_keywords: רשימת מילות מפתח של המותג לסינון
        """
        self.brand_keywords = [kw.lower() for kw in (brand_keywords or [])]

    def remove_brand_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        סינון שאילתות שמכילות מילות מפתח של המותג

        רציונל: שאילתות מותג בדרך כלל כבר מדורגות טוב
        ואין טעם לכתוב עליהן תוכן חדש.

        Args:
            df: DataFrame עם עמודת 'query'

        Returns:
            DataFrame מסונן
        """
        if not self.brand_keywords:
            return df

        df = df.copy()

        # צור pattern regex לכל מילות המותג
        pattern = '|'.join([re.escape(kw) for kw in self.brand_keywords])

        # סנן שורות שמכילות מילות מותג
        mask = ~df['query'].str.lower().str.contains(pattern, na=False)

        filtered_df = df[mask].reset_index(drop=True)

        removed_count = len(df) - len(filtered_df)
        if removed_count > 0:
            print(f"✓ הוסרו {removed_count} שאילתות מותג")

        return filtered_df

    def remove_low_volume_queries(
        self,
        df: pd.DataFrame,
        min_impressions: int = 10,
        min_clicks: int = 0
    ) -> pd.DataFrame:
        """
        סינון שאילתות עם נפח נמוך מדי

        Args:
            df: DataFrame
            min_impressions: מספר חשיפות מינימלי
            min_clicks: מספר קליקים מינימלי

        Returns:
            DataFrame מסונן
        """
        df = df.copy()

        original_count = len(df)

        # סינון
        df = df[
            (df['impressions'] >= min_impressions) &
            (df['clicks'] >= min_clicks)
        ].reset_index(drop=True)

        removed_count = original_count - len(df)
        if removed_count > 0:
            print(f"✓ הוסרו {removed_count} שאילתות עם נפח נמוך")

        return df

    def remove_duplicate_queries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        הסרת שאילתות כפולות (לפי query + page)

        Args:
            df: DataFrame

        Returns:
            DataFrame ללא כפילויות
        """
        df = df.copy()

        original_count = len(df)

        # הסר כפילויות, שמור את השורה עם הכי הרבה קליקים
        df = df.sort_values('clicks', ascending=False)
        df = df.drop_duplicates(subset=['query', 'page'], keep='first')
        df = df.reset_index(drop=True)

        removed_count = original_count - len(df)
        if removed_count > 0:
            print(f"✓ הוסרו {removed_count} שאילתות כפולות")

        return df

    def normalize_queries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        נירמול שאילתות - הסרת רווחים מיותרים, המרה לאותיות קטנות

        Args:
            df: DataFrame

        Returns:
            DataFrame עם שאילתות מנורמלות
        """
        df = df.copy()

        # הסר רווחים מיותרים
        df['query'] = df['query'].str.strip()
        df['query'] = df['query'].str.replace(r'\s+', ' ', regex=True)

        # יצירת עמודה נוספת עם גרסה lowercase (לניתוח)
        df['query_normalized'] = df['query'].str.lower()

        return df

    def filter_question_queries(
        self,
        df: pd.DataFrame,
        include_only: bool = False
    ) -> pd.DataFrame:
        """
        סינון/זיהוי שאילתות שאלה

        Args:
            df: DataFrame
            include_only: אם True, מחזיר רק שאילתות שאלה. אחרת, מוסיף עמודה מזהה.

        Returns:
            DataFrame מעובד
        """
        df = df.copy()

        # מילות שאלה בעברית ואנגלית
        question_words = [
            'איך', 'מה', 'למה', 'מדוע', 'מתי', 'איפה', 'מי', 'כמה',
            'how', 'what', 'why', 'when', 'where', 'who', 'which'
        ]

        # יצור pattern
        pattern = '|'.join([f'\\b{word}\\b' for word in question_words])

        # זהה שאילתות שאלה
        df['is_question'] = df['query'].str.lower().str.contains(
            pattern,
            regex=True,
            na=False
        )

        if include_only:
            df = df[df['is_question']].reset_index(drop=True)
            print(f"✓ נמצאו {len(df)} שאילתות שאלה")

        return df

    def categorize_by_intent(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        קטגוריזציה לפי כוונת חיפוש (Search Intent)

        קטגוריות:
        - Informational: חיפוש מידע
        - Transactional: כוונת קנייה
        - Navigational: חיפוש אתר ספציפי

        Args:
            df: DataFrame

        Returns:
            DataFrame עם עמודת 'intent'
        """
        df = df.copy()

        # מילים שמעידות על כוונה עסקית
        transactional_keywords = [
            'קנייה', 'מחיר', 'עלות', 'הזמנה', 'רכישה', 'קופון', 'הנחה',
            'buy', 'price', 'cost', 'order', 'purchase', 'discount'
        ]

        # מילים שמעידות על חיפוש מידע
        informational_keywords = [
            'מדריך', 'איך', 'מה', 'למה', 'הסבר', 'טיפים',
            'guide', 'how', 'what', 'tutorial', 'tips', 'learn'
        ]

        trans_pattern = '|'.join([re.escape(kw) for kw in transactional_keywords])
        info_pattern = '|'.join([re.escape(kw) for kw in informational_keywords])

        # קטגוריזציה
        df['intent'] = 'navigational'  # ברירת מחדל

        df.loc[
            df['query'].str.lower().str.contains(trans_pattern, na=False),
            'intent'
        ] = 'transactional'

        df.loc[
            df['query'].str.lower().str.contains(info_pattern, na=False),
            'intent'
        ] = 'informational'

        return df

    def clean_pipeline(
        self,
        df: pd.DataFrame,
        remove_brand: bool = True,
        min_impressions: int = 10,
        remove_duplicates: bool = True,
        normalize: bool = True,
        add_question_flag: bool = True,
        add_intent: bool = True
    ) -> pd.DataFrame:
        """
        צינור ניקוי מלא - מפעיל את כל השלבים

        Args:
            df: DataFrame גולמי
            remove_brand: האם להסיר שאילתות מותג
            min_impressions: חשיפות מינימליות
            remove_duplicates: האם להסיר כפילויות
            normalize: האם לנרמל שאילתות
            add_question_flag: האם להוסיף זיהוי שאלות
            add_intent: האם להוסיף זיהוי כוונה

        Returns:
            DataFrame נקי ומעובד
        """
        print("\n=== מתחיל ניקוי נתונים ===\n")

        original_count = len(df)

        if normalize:
            df = self.normalize_queries(df)

        if remove_duplicates:
            df = self.remove_duplicate_queries(df)

        if remove_brand:
            df = self.remove_brand_keywords(df)

        df = self.remove_low_volume_queries(df, min_impressions=min_impressions)

        if add_question_flag:
            df = self.filter_question_queries(df, include_only=False)

        if add_intent:
            df = self.categorize_by_intent(df)

        final_count = len(df)
        print(f"\n✓ ניקוי הושלם: {original_count} → {final_count} שורות")
        print(f"  ({original_count - final_count} שורות הוסרו)\n")

        return df


def clean_gsc_data(
    df: pd.DataFrame,
    brand_keywords: Optional[List[str]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    פונקציית עזר פשוטה לניקוי נתונים

    Args:
        df: DataFrame גולמי מ-GSC
        brand_keywords: רשימת מילות מותג
        **kwargs: פרמטרים נוספים ל-clean_pipeline

    Returns:
        DataFrame נקי
    """
    cleaner = DataCleaner(brand_keywords=brand_keywords)
    return cleaner.clean_pipeline(df, **kwargs)


if __name__ == "__main__":
    """
    בדיקה מהירה של המודול
    """
    print("=== בדיקת מודול ניקוי נתונים ===\n")

    # נתוני דוגמה
    sample_data = pd.DataFrame({
        'query': [
            'מדריך SEO מתחילים',
            '  מדריך SEO מתחילים  ',  # כפילות עם רווחים
            'איך לשפר SEO',
            'שם המותג שלי',
            'קנייה מוצר',
            'מה זה SEO',
            'test query'
        ],
        'page': ['https://example.com/page1'] * 7,
        'clicks': [100, 50, 80, 200, 60, 90, 5],
        'impressions': [1000, 500, 800, 3000, 600, 900, 20],
        'ctr': [0.1, 0.1, 0.1, 0.067, 0.1, 0.1, 0.25],
        'position': [5.0, 5.0, 8.0, 2.0, 12.0, 6.0, 15.0]
    })

    print(f"נתונים מקוריים: {len(sample_data)} שורות\n")

    # ניקוי
    cleaner = DataCleaner(brand_keywords=['שם המותג שלי'])
    cleaned_data = cleaner.clean_pipeline(
        sample_data,
        min_impressions=50
    )

    print("\nנתונים נקיים:")
    print(cleaned_data[['query', 'intent', 'is_question']].to_string())
