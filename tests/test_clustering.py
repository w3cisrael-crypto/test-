"""
בדיקות למודול Clustering
"""
import pytest
import pandas as pd
import sys
from pathlib import Path

# הוסף את תיקיית הבסיס ל-PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logic.clustering import (
    KeywordClusterer,
    cluster_keywords,
    analyze_clusters
)


class TestKeywordClusterer:
    """בדיקות למחלקת KeywordClusterer"""

    def test_init(self):
        """בדיקת אתחול"""
        clusterer = KeywordClusterer()
        assert clusterer.language == 'hebrew'
        assert clusterer.min_cluster_size == 2

    def test_init_custom_params(self):
        """בדיקת אתחול עם פרמטרים מותאמים"""
        clusterer = KeywordClusterer(
            language='english',
            min_cluster_size=3,
            max_clusters=10
        )
        assert clusterer.language == 'english'
        assert clusterer.min_cluster_size == 3
        assert clusterer.max_clusters == 10

    def test_prepare_stopwords_hebrew(self):
        """בדיקת stop words עבריות"""
        clusterer = KeywordClusterer(language='hebrew')
        stopwords = clusterer._prepare_stopwords()
        assert 'של' in stopwords
        assert 'את' in stopwords
        assert len(stopwords) > 0

    def test_prepare_stopwords_english(self):
        """בדיקת stop words אנגליות"""
        clusterer = KeywordClusterer(language='english')
        stopwords = clusterer._prepare_stopwords()
        assert 'the' in stopwords
        assert 'is' in stopwords

    def test_extract_keywords(self):
        """בדיקת חילוץ מילות מפתח"""
        clusterer = KeywordClusterer()

        # מחרוזת עם תווים מיוחדים
        result = clusterer._extract_keywords('מדריך SEO! למתחילים?')
        assert '!' not in result
        assert '?' not in result

        # רווחים מיותרים
        result = clusterer._extract_keywords('מדריך   SEO    למתחילים')
        assert 'מדריך seo למתחילים' == result

    def test_cluster_keywords_basic(self):
        """בדיקת קיבוץ בסיסי"""
        clusterer = KeywordClusterer()

        df = pd.DataFrame({
            'query': [
                'מדריך SEO',
                'מדריך SEO למתחילים',
                'שיווק דיגיטלי',
                'שיווק באינטרנט'
            ],
            'impressions': [1000, 800, 600, 500],
            'clicks': [50, 40, 30, 25],
            'position': [5.0, 6.0, 8.0, 9.0]
        })

        result = clusterer.cluster_keywords(df, n_clusters=2)

        # ודא שהעמודה נוספה
        assert 'cluster_id' in result.columns

        # ודא שיש 2 קלאסטרים
        unique_clusters = result['cluster_id'].nunique()
        assert unique_clusters <= 2

    def test_cluster_keywords_single_item(self):
        """בדיקת קיבוץ עם פריט יחיד"""
        clusterer = KeywordClusterer()

        df = pd.DataFrame({
            'query': ['מדריך SEO'],
            'impressions': [1000],
            'clicks': [50],
            'position': [5.0]
        })

        result = clusterer.cluster_keywords(df)

        # ודא שהעמודה נוספה
        assert 'cluster_id' in result.columns
        assert result['cluster_id'].iloc[0] == 0

    def test_cluster_keywords_auto_clusters(self):
        """בדיקת קביעת מספר קלאסטרים אוטומטי"""
        clusterer = KeywordClusterer()

        df = pd.DataFrame({
            'query': [
                f'מילת מפתח {i}' for i in range(20)
            ],
            'impressions': [1000] * 20,
            'clicks': [50] * 20,
            'position': [5.0] * 20
        })

        # ללא ציון מספר קלאסטרים
        result = clusterer.cluster_keywords(df, n_clusters=None)

        # ודא שנוצרו קלאסטרים
        assert 'cluster_id' in result.columns
        assert result['cluster_id'].nunique() >= 2

    def test_get_cluster_summary(self):
        """בדיקת סיכום קלאסטרים"""
        clusterer = KeywordClusterer()

        df = pd.DataFrame({
            'query': ['q1', 'q2', 'q3', 'q4'],
            'cluster_id': [0, 0, 1, 1],
            'impressions': [1000, 800, 600, 500],
            'clicks': [50, 40, 30, 25],
            'position': [5.0, 6.0, 8.0, 9.0],
            'opportunity_score': [85, 80, 70, 65]
        })

        summary = clusterer.get_cluster_summary(df)

        # ודא שיש 2 קלאסטרים
        assert len(summary) == 2

        # ודא שהעמודות הנכונות קיימות
        assert 'num_keywords' in summary.columns
        assert 'impressions' in summary.columns
        assert 'avg_opportunity_score' in summary.columns

    def test_get_cluster_keywords(self):
        """בדיקת קבלת מילות מפתח לקלאסטר"""
        clusterer = KeywordClusterer()

        df = pd.DataFrame({
            'query': ['q1', 'q2', 'q3', 'q4'],
            'cluster_id': [0, 0, 1, 1],
            'opportunity_score': [85, 80, 70, 65]
        })

        result = clusterer.get_cluster_keywords(df, cluster_id=0, top_n=2)

        # ודא שהוחזרו רק מילות מפתח מקלאסטר 0
        assert all(result['cluster_id'] == 0)
        assert len(result) == 2

        # ודא שממוינות לפי ציון
        assert result.iloc[0]['opportunity_score'] >= result.iloc[1]['opportunity_score']

    def test_suggest_cluster_topic(self):
        """בדיקת הצעת נושא לקלאסטר"""
        clusterer = KeywordClusterer(language='hebrew')

        df = pd.DataFrame({
            'query': ['מדריך SEO', 'מדריך SEO למתחילים', 'מדריך אופטימיזציה'],
            'cluster_id': [0, 0, 0]
        })

        topic = clusterer.suggest_cluster_topic(df, cluster_id=0)

        # ודא שהנושא מכיל מילים רלוונטיות
        assert isinstance(topic, str)
        assert len(topic) > 0


class TestHelperFunctions:
    """בדיקות לפונקציות עזר"""

    def test_cluster_keywords_function(self):
        """בדיקת פונקציית העזר cluster_keywords"""
        df = pd.DataFrame({
            'query': ['q1', 'q2', 'q3', 'q4'],
            'impressions': [1000, 800, 600, 500],
            'clicks': [50, 40, 30, 25],
            'position': [5.0, 6.0, 8.0, 9.0]
        })

        result = cluster_keywords(df, n_clusters=2)

        # ודא שהעמודה נוספה
        assert 'cluster_id' in result.columns

    def test_analyze_clusters(self):
        """בדיקת ניתוח קלאסטרים"""
        df = pd.DataFrame({
            'query': ['q1', 'q2', 'q3', 'q4'],
            'cluster_id': [0, 0, 1, 1],
            'impressions': [1000, 800, 600, 500],
            'clicks': [50, 40, 30, 25],
            'position': [5.0, 6.0, 8.0, 9.0],
            'opportunity_score': [85, 80, 70, 65]
        })

        analysis = analyze_clusters(df)

        # ודא שכל המפתחות הצפויים קיימים
        expected_keys = [
            'num_clusters',
            'avg_keywords_per_cluster',
            'largest_cluster',
            'largest_cluster_size',
            'smallest_cluster_size',
            'total_impressions',
            'avg_position',
            'best_cluster',
            'best_cluster_score'
        ]

        for key in expected_keys:
            assert key in analysis

        # ודא שהערכים נכונים
        assert analysis['num_clusters'] == 2
        assert analysis['avg_keywords_per_cluster'] == 2.0

    def test_analyze_clusters_empty_df(self):
        """בדיקת ניתוח עבור DataFrame ריק"""
        df = pd.DataFrame()
        analysis = analyze_clusters(df)
        assert analysis == {}


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
