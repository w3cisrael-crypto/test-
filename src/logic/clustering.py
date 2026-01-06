"""
Clustering Engine - מנוע קיבוץ מילות מפתח
מודול לקיבוץ מילות מפתח דומות למניעת קניבליזציה ולתכנון תוכן אסטרטגי
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
import re


class KeywordClusterer:
    """
    מחלקה לקיבוץ מילות מפתח דומות
    """

    def __init__(
        self,
        language: str = 'hebrew',
        min_cluster_size: int = 2,
        max_clusters: Optional[int] = None
    ):
        """
        אתחול המנוע

        Args:
            language: שפה ('hebrew', 'english', 'mixed')
            min_cluster_size: גודל מינימלי לקלאסטר תקף
            max_clusters: מספר קלאסטרים מקסימלי (None = אוטומטי)
        """
        self.language = language
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.vectorizer = None
        self.model = None

    def _prepare_stopwords(self) -> List[str]:
        """
        הכנת רשימת Stop words לפי השפה

        Returns:
            רשימת מילים לסינון
        """
        hebrew_stopwords = [
            'של', 'את', 'עם', 'על', 'אל', 'מה', 'זה', 'זאת', 'איך',
            'כל', 'או', 'אבל', 'גם', 'רק', 'עוד', 'כי', 'אם', 'למה',
            'יש', 'היה', 'הוא', 'היא', 'אני', 'אתה', 'הם', 'אנחנו'
        ]

        english_stopwords = [
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are',
            'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may'
        ]

        if self.language == 'hebrew':
            return hebrew_stopwords
        elif self.language == 'english':
            return english_stopwords
        else:  # mixed
            return hebrew_stopwords + english_stopwords

    def _extract_keywords(self, query: str) -> str:
        """
        חילוץ מילות מפתח עיקריות מהשאילתה

        Args:
            query: שאילתה

        Returns:
            מחרוזת מנוקה
        """
        # הסר תווים מיוחדים
        query = re.sub(r'[^\w\s]', ' ', query)

        # המרה לאותיות קטנות
        query = query.lower()

        # הסר רווחים מיותרים
        query = ' '.join(query.split())

        return query

    def determine_optimal_clusters(
        self,
        queries: List[str],
        max_k: Optional[int] = None
    ) -> int:
        """
        קביעת מספר קלאסטרים אוטומטי באמצעות Silhouette Score

        Args:
            queries: רשימת שאילתות
            max_k: מספר קלאסטרים מקסימלי לבדיקה

        Returns:
            מספר קלאסטרים אופטימלי
        """
        if len(queries) < 4:
            return 1

        # הגבל את מספר הקלאסטרים המקסימלי
        if max_k is None:
            max_k = min(len(queries) // 2, 20)

        # וקטוריזציה
        vectorizer = TfidfVectorizer(
            stop_words=self._prepare_stopwords(),
            max_features=100
        )
        X = vectorizer.fit_transform(queries)

        # בדוק מספרי קלאסטרים שונים
        best_k = 2
        best_score = -1

        for k in range(2, max_k + 1):
            if k >= len(queries):
                break

            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(X)

                # חשב Silhouette Score
                score = silhouette_score(X, labels)

                if score > best_score:
                    best_score = score
                    best_k = k

            except Exception:
                continue

        return best_k

    def cluster_keywords(
        self,
        df: pd.DataFrame,
        n_clusters: Optional[int] = None,
        method: str = 'kmeans'
    ) -> pd.DataFrame:
        """
        קיבוץ מילות מפתח לנושאים

        Args:
            df: DataFrame עם עמודת 'query'
            n_clusters: מספר קלאסטרים (None = אוטומטי)
            method: שיטת קיבוץ ('kmeans', 'hierarchical')

        Returns:
            DataFrame עם עמודת 'cluster_id'
        """
        df = df.copy()

        # ניקוי והכנת השאילתות
        queries = df['query'].apply(self._extract_keywords).tolist()

        if len(queries) < 2:
            df['cluster_id'] = 0
            return df

        # קביעת מספר קלאסטרים
        if n_clusters is None:
            n_clusters = self.determine_optimal_clusters(
                queries,
                max_k=self.max_clusters
            )

        n_clusters = min(n_clusters, len(queries))

        # וקטוריזציה
        self.vectorizer = TfidfVectorizer(
            stop_words=self._prepare_stopwords(),
            max_features=200,
            ngram_range=(1, 2)  # תמיכה בביגרמות
        )

        try:
            X = self.vectorizer.fit_transform(queries)
        except ValueError:
            # אם הוקטוריזציה נכשלת, הכנס הכל לקלאסטר אחד
            df['cluster_id'] = 0
            return df

        # קיבוץ
        if method == 'kmeans':
            self.model = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
        elif method == 'hierarchical':
            self.model = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward'
            )
        else:
            raise ValueError(f"שיטה לא ידועה: {method}")

        # התאמה וחיזוי
        labels = self.model.fit_predict(X)
        df['cluster_id'] = labels

        print(f"✓ נוצרו {n_clusters} קלאסטרים")

        return df

    def get_cluster_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        יצירת סיכום לכל קלאסטר

        Args:
            df: DataFrame עם cluster_id ו-opportunity_score

        Returns:
            DataFrame עם סיכום לכל קלאסטר
        """
        if 'cluster_id' not in df.columns:
            raise ValueError("DataFrame חייב להכיל עמודת cluster_id")

        summary = df.groupby('cluster_id').agg({
            'query': 'count',
            'impressions': 'sum',
            'clicks': 'sum',
            'position': 'mean',
        }).rename(columns={'query': 'num_keywords'})

        # הוסף ציון ממוצע אם קיים
        if 'opportunity_score' in df.columns:
            summary['avg_opportunity_score'] = df.groupby('cluster_id')[
                'opportunity_score'
            ].mean()

        # מיין לפי ציון ממוצע (אם קיים) או לפי סכום חשיפות
        if 'avg_opportunity_score' in summary.columns:
            summary = summary.sort_values(
                'avg_opportunity_score',
                ascending=False
            )
        else:
            summary = summary.sort_values('impressions', ascending=False)

        return summary

    def get_cluster_keywords(
        self,
        df: pd.DataFrame,
        cluster_id: int,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        קבל את מילות המפתח המובילות בקלאסטר

        Args:
            df: DataFrame עם cluster_id
            cluster_id: מזהה הקלאסטר
            top_n: מספר מילות מפתח להחזיר

        Returns:
            DataFrame עם המילים המובילות
        """
        cluster_df = df[df['cluster_id'] == cluster_id].copy()

        # מיין לפי ציון הזדמנות (אם קיים) או לפי קליקים
        if 'opportunity_score' in cluster_df.columns:
            cluster_df = cluster_df.sort_values(
                'opportunity_score',
                ascending=False
            )
        else:
            cluster_df = cluster_df.sort_values('clicks', ascending=False)

        return cluster_df.head(top_n)

    def suggest_cluster_topic(
        self,
        df: pd.DataFrame,
        cluster_id: int,
        top_words: int = 5
    ) -> str:
        """
        הצע נושא לקלאסטר על בסיס המילים השכיחות

        Args:
            df: DataFrame עם cluster_id
            cluster_id: מזהה הקלאסטר
            top_words: מספר מילים לכלול בנושא

        Returns:
            הצעה לנושא הקלאסטר
        """
        cluster_df = df[df['cluster_id'] == cluster_id]

        if cluster_df.empty:
            return f"קלאסטר {cluster_id}"

        # איחוד כל השאילתות
        all_queries = ' '.join(cluster_df['query'].tolist())

        # חילוץ מילים
        words = all_queries.lower().split()

        # ספירת תדירות (ללא stop words)
        stopwords = set(self._prepare_stopwords())
        word_freq = {}

        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1

        # מיין לפי תדירות
        sorted_words = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # קח את המילים השכיחות ביותר
        top_words_list = [word for word, freq in sorted_words[:top_words]]

        return ' '.join(top_words_list)


def cluster_keywords(
    df: pd.DataFrame,
    n_clusters: Optional[int] = None,
    language: str = 'hebrew'
) -> pd.DataFrame:
    """
    פונקציית עזר פשוטה לקיבוץ (תואמת את התוכנית המקורית)

    Args:
        df: DataFrame עם נתוני מילות מפתח
        n_clusters: מספר קלאסטרים (None = אוטומטי)
        language: שפה

    Returns:
        DataFrame עם עמודת cluster_id
    """
    clusterer = KeywordClusterer(language=language)
    return clusterer.cluster_keywords(df, n_clusters=n_clusters)


def analyze_clusters(df: pd.DataFrame) -> Dict:
    """
    ניתוח מקיף של הקלאסטרים

    Args:
        df: DataFrame עם cluster_id

    Returns:
        מילון עם סטטיסטיקות
    """
    if 'cluster_id' not in df.columns:
        return {}

    clusterer = KeywordClusterer()
    summary = clusterer.get_cluster_summary(df)

    analysis = {
        'num_clusters': len(summary),
        'avg_keywords_per_cluster': summary['num_keywords'].mean(),
        'largest_cluster': summary['num_keywords'].idxmax(),
        'largest_cluster_size': summary['num_keywords'].max(),
        'smallest_cluster_size': summary['num_keywords'].min(),
        'total_impressions': summary['impressions'].sum(),
        'avg_position': summary['position'].mean(),
    }

    if 'avg_opportunity_score' in summary.columns:
        analysis['best_cluster'] = summary['avg_opportunity_score'].idxmax()
        analysis['best_cluster_score'] = summary['avg_opportunity_score'].max()

    return analysis


if __name__ == "__main__":
    """
    בדיקה מהירה של המודול
    """
    print("=== בדיקת מנוע הקיבוץ ===\n")

    # יצירת נתוני דוגמה
    sample_data = pd.DataFrame({
        'query': [
            'מדריך SEO למתחילים',
            'מדריך SEO לאתרים',
            'איך לעשות SEO',
            'שיווק דיגיטלי למתחילים',
            'שיווק דיגיטלי באינטרנט',
            'פרסום ממומן גוגל',
            'פרסום ממומן פייסבוק',
            'תוכן שיווקי איכותי',
            'כתיבת תוכן SEO',
            'אופטימיזציה למנועי חיפוש'
        ],
        'impressions': [2000, 1500, 1800, 1200, 1000, 900, 800, 600, 700, 1100],
        'clicks': [150, 120, 140, 90, 80, 70, 65, 50, 60, 85],
        'position': [5.2, 6.1, 5.8, 8.3, 9.1, 11.2, 12.5, 10.3, 7.4, 6.8],
        'opportunity_score': [85, 82, 83, 75, 72, 68, 65, 70, 78, 80]
    })

    # קיבוץ
    clusterer = KeywordClusterer(language='hebrew')
    clustered_data = clusterer.cluster_keywords(sample_data, n_clusters=3)

    print("\n=== תוצאות קיבוץ ===")
    print(clustered_data[['query', 'cluster_id', 'opportunity_score']].to_string())

    # סיכום קלאסטרים
    print("\n=== סיכום קלאסטרים ===")
    summary = clusterer.get_cluster_summary(clustered_data)
    print(summary.to_string())

    # הצעות נושאים
    print("\n=== הצעות נושאים לקלאסטרים ===")
    for cluster_id in clustered_data['cluster_id'].unique():
        topic = clusterer.suggest_cluster_topic(clustered_data, cluster_id)
        print(f"קלאסטר {cluster_id}: {topic}")

    # ניתוח
    print("\n=== ניתוח כללי ===")
    analysis = analyze_clusters(clustered_data)
    for key, value in analysis.items():
        print(f"{key}: {value}")
