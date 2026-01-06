"""
Scoring Engine - מנוע ניקוד והמלצות
מודול לחישוב ציון הזדמנות (Opportunity Score) לכל מילת מפתח

הלוגיקה:
1. פוטנציאל טראפיק (40%) - מבוסס על מספר חשיפות
2. מרחק נגיעה (40%) - מבוסס על מיקום בתוצאות
3. Quick Wins (20%) - זיהוי CTR נמוך ביחס למיקום
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional


class OpportunityScorer:
    """
    מחלקה לחישוב ציוני הזדמנות למילות מפתח
    """

    # טבלת CTR צפוי לפי מיקום (מבוסס על מחקרים בתעשייה)
    EXPECTED_CTR = {
        1: 0.30,   # מיקום 1 - ~30% CTR
        2: 0.15,   # מיקום 2 - ~15% CTR
        3: 0.10,   # מיקום 3 - ~10% CTR
        4: 0.07,   # מיקום 4 - ~7% CTR
        5: 0.05,   # מיקום 5 - ~5% CTR
        6: 0.04,   # מיקום 6 - ~4% CTR
        7: 0.03,   # מיקום 7 - ~3% CTR
        8: 0.025,  # מיקום 8 - ~2.5% CTR
        9: 0.02,   # מיקום 9 - ~2% CTR
        10: 0.015, # מיקום 10 - ~1.5% CTR
    }

    def __init__(
        self,
        traffic_weight: float = 0.4,
        position_weight: float = 0.4,
        quick_wins_weight: float = 0.2
    ):
        """
        אתחול המנוע

        Args:
            traffic_weight: משקל רכיב פוטנציאל הטראפיק (ברירת מחדל: 0.4)
            position_weight: משקל רכיב המיקום (ברירת מחדל: 0.4)
            quick_wins_weight: משקל רכיב Quick Wins (ברירת מחדל: 0.2)
        """
        # וידוא שהמשקולות מסתכמות ל-1
        total = traffic_weight + position_weight + quick_wins_weight
        if not np.isclose(total, 1.0):
            raise ValueError(f"סכום המשקולות חייב להיות 1.0 (קיבלתי: {total})")

        self.traffic_weight = traffic_weight
        self.position_weight = position_weight
        self.quick_wins_weight = quick_wins_weight

    def calculate_traffic_score(self, impressions: int) -> float:
        """
        חישוב ציון פוטנציאל טראפיק (0-100)

        Args:
            impressions: מספר החשיפות

        Returns:
            ציון בין 0 ל-100
        """
        if impressions >= 5000:
            return 100.0
        elif impressions >= 2000:
            return 90.0
        elif impressions >= 1000:
            return 75.0
        elif impressions >= 500:
            return 60.0
        elif impressions >= 250:
            return 45.0
        elif impressions >= 100:
            return 30.0
        elif impressions >= 50:
            return 15.0
        else:
            return 5.0

    def calculate_position_score(self, position: float) -> float:
        """
        חישוב ציון מיקום - "מרחק נגיעה" (0-100)

        ההיגיון:
        - מיקומים 4-10: פוטנציאל גבוה (כבר בעמוד 1, אפשר לשפר)
        - מיקומים 11-20: פוטנציאל בינוני (עמוד 2, אפשר להביא לעמוד 1)
        - מיקומים 21-30: פוטנציאל נמוך-בינוני (עמוד 3)
        - מיקומים 31+: פוטנציאל נמוך

        Args:
            position: מיקום ממוצע בתוצאות החיפוש

        Returns:
            ציון בין 0 ל-100
        """
        if position <= 3:
            # מיקומים 1-3: כבר מצוינים, פחות פוטנציאל לשיפור
            return 50.0
        elif position <= 10:
            # מיקומים 4-10: הזדמנות מעולה - תחתית עמוד 1
            return 100.0
        elif position <= 15:
            # מיקומים 11-15: הזדמנות טובה מאוד - ראש עמוד 2
            return 85.0
        elif position <= 20:
            # מיקומים 16-20: הזדמנות טובה - תחתית עמוד 2
            return 70.0
        elif position <= 30:
            # מיקומים 21-30: הזדמנות בינונית - עמוד 3
            return 40.0
        elif position <= 50:
            # מיקומים 31-50: פוטנציאל נמוך
            return 20.0
        else:
            # מיקום 51+: פוטנציאל מינימלי
            return 5.0

    def calculate_quick_wins_score(
        self,
        position: float,
        ctr: float,
        impressions: int
    ) -> float:
        """
        חישוב ציון Quick Wins - זיהוי הזדמנויות מהירות (0-100)

        מזהה מקרים שבהם CTR נמוך ביחס למיקום,
        מה שמעיד על בעיה בכותרת, meta description או תוכן הדף.

        Args:
            position: מיקום בתוצאות
            ctr: Click Through Rate בפועל
            impressions: מספר חשיפות (לסינון רעש סטטיסטי)

        Returns:
            ציון בין 0 ל-100
        """
        # דרוש מינימום חשיפות לאמינות סטטיסטית
        if impressions < 50:
            return 0.0

        # רק עבור מיקומים בעמוד הראשון (1-10)
        if position > 10:
            return 0.0

        # קבל CTR צפוי
        rounded_position = int(round(position))
        expected_ctr = self.EXPECTED_CTR.get(
            rounded_position,
            0.01  # ברירת מחדל למיקומים שאינם בטבלה
        )

        # חשב פער
        ctr_gap = expected_ctr - ctr

        # אם ה-CTR בפועל טוב מהצפוי, אין Quick Win
        if ctr_gap <= 0:
            return 0.0

        # חשב ציון לפי גודל הפער
        gap_ratio = ctr_gap / expected_ctr

        if gap_ratio >= 0.5:  # פער של 50% ומעלה
            return 100.0
        elif gap_ratio >= 0.3:  # פער של 30-50%
            return 80.0
        elif gap_ratio >= 0.2:  # פער של 20-30%
            return 60.0
        elif gap_ratio >= 0.1:  # פער של 10-20%
            return 40.0
        else:  # פער קטן מ-10%
            return 20.0

    def calculate_opportunity_score(self, row: pd.Series) -> float:
        """
        חישוב ציון ההזדמנות הכולל (0-100)

        Args:
            row: שורה מ-DataFrame עם הנתונים הבאים:
                - position: מיקום ממוצע
                - impressions: מספר חשיפות
                - ctr: Click Through Rate
                - clicks: מספר קליקים

        Returns:
            ציון כולל בין 0 ל-100
        """
        # חישוב רכיבי הציון
        traffic_score = self.calculate_traffic_score(row['impressions'])
        position_score = self.calculate_position_score(row['position'])
        quick_wins_score = self.calculate_quick_wins_score(
            row['position'],
            row['ctr'],
            row['impressions']
        )

        # חישוב ממוצע משוקלל
        total_score = (
            traffic_score * self.traffic_weight +
            position_score * self.position_weight +
            quick_wins_score * self.quick_wins_weight
        )

        return round(total_score, 2)

    def score_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        הוספת ציוני הזדמנות לכל השורות ב-DataFrame

        Args:
            df: DataFrame עם נתוני GSC

        Returns:
            DataFrame עם עמודות נוספות:
                - traffic_score
                - position_score
                - quick_wins_score
                - opportunity_score
        """
        df = df.copy()

        # חישוב כל רכיבי הציון
        df['traffic_score'] = df['impressions'].apply(self.calculate_traffic_score)
        df['position_score'] = df['position'].apply(self.calculate_position_score)
        df['quick_wins_score'] = df.apply(
            lambda row: self.calculate_quick_wins_score(
                row['position'],
                row['ctr'],
                row['impressions']
            ),
            axis=1
        )

        # חישוב הציון הכולל
        df['opportunity_score'] = df.apply(self.calculate_opportunity_score, axis=1)

        return df


def calculate_opportunity_score(row: pd.Series) -> float:
    """
    פונקציית עזר פשוטה לחישוב ציון (תואמת את התוכנית המקורית)

    Args:
        row: שורה עם נתוני מילת מפתח

    Returns:
        ציון הזדמנות בין 0 ל-100
    """
    scorer = OpportunityScorer()
    return scorer.calculate_opportunity_score(row)


def rank_opportunities(
    df: pd.DataFrame,
    top_n: Optional[int] = None,
    min_score: float = 0.0
) -> pd.DataFrame:
    """
    דירוג והצגת ההזדמנויות הטובות ביותר

    Args:
        df: DataFrame עם נתוני GSC
        top_n: מספר התוצאות המקסימלי להחזיר (None = הכל)
        min_score: ציון מינימלי לסינון

    Returns:
        DataFrame ממוין לפי opportunity_score
    """
    scorer = OpportunityScorer()

    # הוסף ציונים אם עדיין אין
    if 'opportunity_score' not in df.columns:
        df = scorer.score_dataframe(df)

    # סנן לפי ציון מינימלי
    df_filtered = df[df['opportunity_score'] >= min_score].copy()

    # מיין לפי ציון (יורד)
    df_sorted = df_filtered.sort_values(
        by='opportunity_score',
        ascending=False
    ).reset_index(drop=True)

    # הגבל מספר תוצאות אם נדרש
    if top_n:
        df_sorted = df_sorted.head(top_n)

    return df_sorted


def get_opportunity_insights(df: pd.DataFrame) -> Dict:
    """
    ניתוח והפקת תובנות מהנתונים

    Args:
        df: DataFrame עם ציוני הזדמנות

    Returns:
        מילון עם תובנות סטטיסטיות
    """
    if df.empty or 'opportunity_score' not in df.columns:
        return {}

    insights = {
        'total_opportunities': len(df),
        'avg_score': df['opportunity_score'].mean(),
        'median_score': df['opportunity_score'].median(),
        'high_opportunities': len(df[df['opportunity_score'] >= 75]),
        'medium_opportunities': len(df[
            (df['opportunity_score'] >= 50) &
            (df['opportunity_score'] < 75)
        ]),
        'low_opportunities': len(df[df['opportunity_score'] < 50]),
        'quick_wins': len(df[df['quick_wins_score'] > 50]),
        'page_2_keywords': len(df[
            (df['position'] >= 11) & (df['position'] <= 20)
        ]),
        'total_potential_impressions': df['impressions'].sum(),
        'total_potential_clicks': df['clicks'].sum(),
    }

    return insights


if __name__ == "__main__":
    """
    בדיקה מהירה של המודול
    """
    print("=== בדיקת מנוע הניקוד ===\n")

    # יצירת נתוני דוגמה
    sample_data = pd.DataFrame({
        'query': [
            'מדריך SEO מתחילים',
            'שיווק דיגיטלי',
            'אופטימיזציה אתרים',
            'תוכן איכותי',
            'מילות מפתח'
        ],
        'page': ['https://example.com/page1'] * 5,
        'clicks': [150, 80, 200, 50, 30],
        'impressions': [2000, 1500, 3000, 800, 500],
        'ctr': [0.075, 0.053, 0.067, 0.0625, 0.06],
        'position': [5.2, 12.5, 8.1, 15.3, 18.7]
    })

    # חישוב ציונים
    scorer = OpportunityScorer()
    scored_data = scorer.score_dataframe(sample_data)

    print("נתונים עם ציונים:")
    print(scored_data[[
        'query', 'position', 'impressions', 'ctr',
        'opportunity_score', 'quick_wins_score'
    ]].to_string())

    # דירוג
    print("\n=== דירוג הזדמנויות ===")
    ranked = rank_opportunities(scored_data, top_n=3)
    print(ranked[['query', 'opportunity_score', 'position']].to_string())

    # תובנות
    print("\n=== תובנות ===")
    insights = get_opportunity_insights(scored_data)
    for key, value in insights.items():
        print(f"{key}: {value}")
