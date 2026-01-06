"""
בדיקות למודול Scoring Engine
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# הוסף את תיקיית הבסיס ל-PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logic.scoring import (
    OpportunityScorer,
    calculate_opportunity_score,
    rank_opportunities,
    get_opportunity_insights
)


class TestOpportunityScorer:
    """בדיקות למחלקת OpportunityScorer"""

    def test_init_default_weights(self):
        """בדיקת אתחול עם משקולות ברירת מחדל"""
        scorer = OpportunityScorer()
        assert scorer.traffic_weight == 0.4
        assert scorer.position_weight == 0.4
        assert scorer.quick_wins_weight == 0.2

    def test_init_custom_weights(self):
        """בדיקת אתחול עם משקולות מותאמות אישית"""
        scorer = OpportunityScorer(
            traffic_weight=0.5,
            position_weight=0.3,
            quick_wins_weight=0.2
        )
        assert scorer.traffic_weight == 0.5
        assert scorer.position_weight == 0.3
        assert scorer.quick_wins_weight == 0.2

    def test_init_invalid_weights(self):
        """בדיקת טיפול במשקולות לא חוקיות"""
        with pytest.raises(ValueError):
            OpportunityScorer(
                traffic_weight=0.5,
                position_weight=0.5,
                quick_wins_weight=0.5  # סכום > 1
            )

    def test_calculate_traffic_score(self):
        """בדיקת חישוב ציון טראפיק"""
        scorer = OpportunityScorer()

        # חשיפות גבוהות מאוד
        assert scorer.calculate_traffic_score(5000) == 100.0

        # חשיפות בינוניות
        assert scorer.calculate_traffic_score(1000) == 75.0

        # חשיפות נמוכות
        assert scorer.calculate_traffic_score(50) == 15.0

    def test_calculate_position_score(self):
        """בדיקת חישוב ציון מיקום"""
        scorer = OpportunityScorer()

        # מיקום מצוין (1-3) - ציון נמוך יותר (פחות פוטנציאל)
        assert scorer.calculate_position_score(2.0) == 50.0

        # מיקום מעולה לשיפור (4-10) - ציון גבוה
        assert scorer.calculate_position_score(8.0) == 100.0

        # עמוד 2 (11-20)
        assert scorer.calculate_position_score(15.0) == 85.0

        # מיקום רחוק
        assert scorer.calculate_position_score(55.0) == 5.0

    def test_calculate_quick_wins_score(self):
        """בדיקת חישוב ציון Quick Wins"""
        scorer = OpportunityScorer()

        # CTR נמוך ביחס למיקום - Quick Win
        score = scorer.calculate_quick_wins_score(
            position=5.0,
            ctr=0.02,  # CTR נמוך מאוד למיקום 5
            impressions=1000
        )
        assert score > 50.0

        # CTR טוב ביחס למיקום - אין Quick Win
        score = scorer.calculate_quick_wins_score(
            position=5.0,
            ctr=0.06,  # CTR סביר למיקום 5
            impressions=1000
        )
        assert score == 0.0

        # מעט חשיפות - אין אמינות סטטיסטית
        score = scorer.calculate_quick_wins_score(
            position=5.0,
            ctr=0.01,
            impressions=30  # מעט מדי
        )
        assert score == 0.0

        # מיקום מחוץ לעמוד 1 - אין Quick Win
        score = scorer.calculate_quick_wins_score(
            position=15.0,
            ctr=0.01,
            impressions=1000
        )
        assert score == 0.0

    def test_calculate_opportunity_score(self):
        """בדיקת חישוב ציון הזדמנות כולל"""
        scorer = OpportunityScorer()

        row = pd.Series({
            'position': 8.0,
            'impressions': 1000,
            'ctr': 0.02,
            'clicks': 20
        })

        score = scorer.calculate_opportunity_score(row)

        # ודא שהציון בטווח תקין
        assert 0 <= score <= 100

        # ודא שהציון הוא מספר עם 2 ספרות אחרי הנקודה
        assert score == round(score, 2)

    def test_score_dataframe(self):
        """בדיקת הוספת ציונים ל-DataFrame"""
        scorer = OpportunityScorer()

        df = pd.DataFrame({
            'query': ['test1', 'test2'],
            'position': [5.0, 15.0],
            'impressions': [1000, 500],
            'ctr': [0.03, 0.02],
            'clicks': [30, 10]
        })

        df_scored = scorer.score_dataframe(df)

        # ודא שהעמודות החדשות נוספו
        assert 'traffic_score' in df_scored.columns
        assert 'position_score' in df_scored.columns
        assert 'quick_wins_score' in df_scored.columns
        assert 'opportunity_score' in df_scored.columns

        # ודא שכל הציונים בטווח תקין
        assert all(0 <= score <= 100 for score in df_scored['opportunity_score'])


class TestHelperFunctions:
    """בדיקות לפונקציות עזר"""

    def test_calculate_opportunity_score_function(self):
        """בדיקת פונקציית העזר calculate_opportunity_score"""
        row = pd.Series({
            'position': 8.0,
            'impressions': 1000,
            'ctr': 0.02,
            'clicks': 20
        })

        score = calculate_opportunity_score(row)
        assert 0 <= score <= 100

    def test_rank_opportunities(self):
        """בדיקת דירוג הזדמנויות"""
        df = pd.DataFrame({
            'query': ['query1', 'query2', 'query3'],
            'position': [5.0, 15.0, 8.0],
            'impressions': [1000, 500, 2000],
            'ctr': [0.03, 0.02, 0.04],
            'clicks': [30, 10, 80]
        })

        ranked_df = rank_opportunities(df)

        # ודא שהעמודה opportunity_score נוספה
        assert 'opportunity_score' in ranked_df.columns

        # ודא שהתוצאות ממוינות יורד
        scores = ranked_df['opportunity_score'].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_rank_opportunities_with_limit(self):
        """בדיקת דירוג עם הגבלת תוצאות"""
        df = pd.DataFrame({
            'query': [f'query{i}' for i in range(10)],
            'position': [5.0 + i for i in range(10)],
            'impressions': [1000] * 10,
            'ctr': [0.03] * 10,
            'clicks': [30] * 10
        })

        ranked_df = rank_opportunities(df, top_n=3)

        # ודא שהוחזרו רק 3 תוצאות
        assert len(ranked_df) == 3

    def test_rank_opportunities_with_min_score(self):
        """בדיקת דירוג עם ציון מינימלי"""
        df = pd.DataFrame({
            'query': ['high', 'medium', 'low'],
            'position': [5.0, 15.0, 50.0],
            'impressions': [5000, 1000, 50],
            'ctr': [0.03, 0.02, 0.01],
            'clicks': [150, 20, 1]
        })

        ranked_df = rank_opportunities(df, min_score=60.0)

        # ודא שכל הציונים מעל המינימום
        assert all(score >= 60.0 for score in ranked_df['opportunity_score'])

    def test_get_opportunity_insights(self):
        """בדיקת חילוץ תובנות"""
        df = pd.DataFrame({
            'query': ['q1', 'q2', 'q3'],
            'position': [5.0, 12.0, 18.0],
            'impressions': [1000, 500, 300],
            'ctr': [0.03, 0.02, 0.015],
            'clicks': [30, 10, 5]
        })

        scorer = OpportunityScorer()
        df_scored = scorer.score_dataframe(df)

        insights = get_opportunity_insights(df_scored)

        # ודא שכל המפתחות הצפויים קיימים
        expected_keys = [
            'total_opportunities',
            'avg_score',
            'median_score',
            'high_opportunities',
            'medium_opportunities',
            'low_opportunities',
            'quick_wins',
            'page_2_keywords',
            'total_potential_impressions',
            'total_potential_clicks'
        ]

        for key in expected_keys:
            assert key in insights

        # ודא שהסטטיסטיקות נכונות
        assert insights['total_opportunities'] == 3
        assert insights['page_2_keywords'] == 2  # שתי שאילתות במיקומים 11-20

    def test_get_opportunity_insights_empty_df(self):
        """בדיקת תובנות עבור DataFrame ריק"""
        df = pd.DataFrame()
        insights = get_opportunity_insights(df)
        assert insights == {}


class TestEdgeCases:
    """בדיקות למקרי קצה"""

    def test_zero_impressions(self):
        """בדיקת טיפול באפס חשיפות"""
        scorer = OpportunityScorer()
        score = scorer.calculate_traffic_score(0)
        assert score == 5.0  # ציון מינימלי

    def test_extreme_position(self):
        """בדיקת טיפול במיקום קיצוני"""
        scorer = OpportunityScorer()
        score = scorer.calculate_position_score(100.0)
        assert score == 5.0  # ציון מינימלי

    def test_ctr_above_expected(self):
        """בדיקת CTR מעל הצפוי"""
        scorer = OpportunityScorer()
        score = scorer.calculate_quick_wins_score(
            position=1.0,
            ctr=0.50,  # CTR מעולה
            impressions=1000
        )
        assert score == 0.0  # אין צורך בשיפור


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
