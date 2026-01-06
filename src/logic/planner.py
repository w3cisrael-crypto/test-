"""
Planning Engine - מנוע תכנון תוכן
מודול לבניית תוכנית תוכן חודשית אסטרטגית
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from .clustering import KeywordClusterer, cluster_keywords
from .scoring import OpportunityScorer


class ContentPlanner:
    """
    מחלקה לתכנון תוכן חודשי מבוסס נתונים
    """

    def __init__(
        self,
        pillar_ratio: float = 0.3,
        cluster_ratio: float = 0.7
    ):
        """
        אתחול המתכנן

        Args:
            pillar_ratio: יחס מאמרי Pillar מסך המאמרים (ברירת מחדל: 30%)
            cluster_ratio: יחס מאמרי Cluster מסך המאמרים (ברירת מחדל: 70%)
        """
        if not np.isclose(pillar_ratio + cluster_ratio, 1.0):
            raise ValueError("סכום היחסים חייב להיות 1.0")

        self.pillar_ratio = pillar_ratio
        self.cluster_ratio = cluster_ratio

    def _identify_pillar_keywords(
        self,
        df: pd.DataFrame,
        top_n: int = 3
    ) -> pd.DataFrame:
        """
        זיהוי מילות מפתח ראשיות (Pillar) לכל קלאסטר

        Args:
            df: DataFrame עם cluster_id ו-opportunity_score
            top_n: מספר Pillars לכל קלאסטר

        Returns:
            DataFrame עם מילות מפתח Pillar
        """
        pillar_keywords = []

        for cluster_id in df['cluster_id'].unique():
            cluster_df = df[df['cluster_id'] == cluster_id]

            # בחר את הטובות ביותר לפי ציון
            top_in_cluster = cluster_df.nlargest(
                top_n,
                'opportunity_score'
            )

            pillar_keywords.append(top_in_cluster)

        if pillar_keywords:
            return pd.concat(pillar_keywords, ignore_index=True)
        else:
            return pd.DataFrame()

    def _identify_cluster_keywords(
        self,
        df: pd.DataFrame,
        pillar_df: pd.DataFrame,
        num_articles: int
    ) -> pd.DataFrame:
        """
        זיהוי מילות מפתח תומכות (Cluster)

        Args:
            df: DataFrame עם כל מילות המפתח
            pillar_df: DataFrame עם Pillar keywords
            num_articles: מספר מאמרי Cluster לבחור

        Returns:
            DataFrame עם מילות מפתח Cluster
        """
        # הוצא את ה-Pillars
        remaining_df = df[
            ~df.index.isin(pillar_df.index)
        ].copy()

        # בחר את הטובים ביותר שנותרו
        cluster_keywords = remaining_df.nlargest(
            num_articles,
            'opportunity_score'
        )

        return cluster_keywords

    def generate_monthly_plan(
        self,
        df: pd.DataFrame,
        num_articles: int = 12,
        strategy: str = 'balanced'
    ) -> Dict:
        """
        יצירת תוכנית תוכן חודשית

        Args:
            df: DataFrame עם נתונים מנוקים וציונים
            num_articles: מספר מאמרים לחודש
            strategy: אסטרטגיית בחירה:
                - 'balanced': איזון בין Pillar ל-Cluster
                - 'pillar_focused': דגש על Pillar (50/50)
                - 'quick_wins': התמקדות ב-Quick Wins

        Returns:
            מילון עם התוכנית המלאה
        """
        df = df.copy()

        # ודא שיש cluster_id
        if 'cluster_id' not in df.columns:
            print("⚠ לא נמצא cluster_id, מבצע קיבוץ אוטומטי...")
            clusterer = KeywordClusterer()
            df = clusterer.cluster_keywords(df)

        # התאם יחסים לפי אסטרטגיה
        if strategy == 'pillar_focused':
            pillar_ratio = 0.5
            cluster_ratio = 0.5
        elif strategy == 'quick_wins':
            # התמקד במילות מפתח עם Quick Wins גבוה
            df = df.sort_values('quick_wins_score', ascending=False)
            pillar_ratio = 0.3
            cluster_ratio = 0.7
        else:  # balanced
            pillar_ratio = self.pillar_ratio
            cluster_ratio = self.cluster_ratio

        # חשב מספר מאמרים מכל סוג
        num_pillars = max(1, int(num_articles * pillar_ratio))
        num_clusters = num_articles - num_pillars

        # זהה Pillar keywords
        pillar_df = self._identify_pillar_keywords(df, top_n=1)

        # אם יש יותר מדי Pillars, קח רק את הטובים ביותר
        if len(pillar_df) > num_pillars:
            pillar_df = pillar_df.nlargest(num_pillars, 'opportunity_score')

        # זהה Cluster keywords
        cluster_df = self._identify_cluster_keywords(
            df,
            pillar_df,
            num_clusters
        )

        # סמן את הסוג
        pillar_df = pillar_df.copy()
        cluster_df = cluster_df.copy()
        pillar_df['content_type'] = 'Pillar'
        cluster_df['content_type'] = 'Cluster'

        # איחוד
        plan_df = pd.concat([pillar_df, cluster_df], ignore_index=True)

        # מיין לפי ציון
        plan_df = plan_df.sort_values('opportunity_score', ascending=False)

        # הוסף עדיפות
        plan_df['priority'] = range(1, len(plan_df) + 1)

        # סיכום
        summary = {
            'total_articles': len(plan_df),
            'pillar_articles': len(pillar_df),
            'cluster_articles': len(cluster_df),
            'num_clusters': df['cluster_id'].nunique(),
            'avg_opportunity_score': plan_df['opportunity_score'].mean(),
            'total_potential_impressions': plan_df['impressions'].sum(),
            'total_potential_clicks': plan_df['clicks'].sum(),
            'strategy': strategy,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return {
            'plan': plan_df,
            'summary': summary,
            'cluster_distribution': plan_df.groupby('cluster_id').size().to_dict()
        }

    def suggest_publishing_schedule(
        self,
        plan_df: pd.DataFrame,
        start_date: Optional[str] = None,
        posts_per_week: int = 3
    ) -> pd.DataFrame:
        """
        הצעת לוח זמנים לפרסום

        Args:
            plan_df: DataFrame עם התוכנית
            start_date: תאריך התחלה (YYYY-MM-DD)
            posts_per_week: מספר פוסטים בשבוע

        Returns:
            DataFrame עם תאריכי פרסום מוצעים
        """
        plan_df = plan_df.copy()

        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')

        # חשב מרווח ימים בין פוסטים
        days_between = 7 // posts_per_week

        # הוסף תאריכים
        dates = pd.date_range(
            start=start_date,
            periods=len(plan_df),
            freq=f'{days_between}D'
        )

        plan_df['suggested_date'] = dates
        plan_df['week'] = (plan_df.index // posts_per_week) + 1

        return plan_df

    def create_content_briefs(
        self,
        plan_df: pd.DataFrame,
        clusterer: Optional[KeywordClusterer] = None
    ) -> List[Dict]:
        """
        יצירת בריפים לכל מאמר בתוכנית

        Args:
            plan_df: DataFrame עם התוכנית
            clusterer: אובייקט KeywordClusterer (אופציונלי)

        Returns:
            רשימת בריפים
        """
        briefs = []

        for idx, row in plan_df.iterrows():
            brief = {
                'priority': row.get('priority', idx + 1),
                'main_keyword': row['query'],
                'content_type': row.get('content_type', 'Unknown'),
                'cluster_id': row.get('cluster_id', 0),
                'opportunity_score': row.get('opportunity_score', 0),
                'current_position': row.get('position', 0),
                'monthly_impressions': row.get('impressions', 0),
                'monthly_clicks': row.get('clicks', 0),
                'current_ctr': row.get('ctr', 0),
                'target_position': max(1, row.get('position', 10) - 3),
            }

            # המלצות
            if row.get('content_type') == 'Pillar':
                brief['recommended_length'] = '2000-3000 מילים'
                brief['content_depth'] = 'מקיף ומעמיק'
                brief['internal_links'] = 'קישורים למאמרי Cluster רלוונטיים'
            else:
                brief['recommended_length'] = '1000-1500 מילים'
                brief['content_depth'] = 'ממוקד ופרקטי'
                brief['internal_links'] = 'קישור למאמר Pillar הראשי'

            # המלצות ספציפיות לפי ציון
            if row.get('quick_wins_score', 0) > 50:
                brief['action'] = 'שפר Title ו-Meta Description לשיפור CTR'
            elif row.get('position', 100) <= 10:
                brief['action'] = 'עדכן ושפר את הדף הקיים'
            elif row.get('position', 100) <= 20:
                brief['action'] = 'צור תוכן מקיף חדש'
            else:
                brief['action'] = 'צור תוכן Pillar איכותי'

            # הוסף תאריך אם קיים
            if 'suggested_date' in row:
                brief['suggested_date'] = row['suggested_date'].strftime('%Y-%m-%d')

            briefs.append(brief)

        return briefs


def generate_monthly_plan(
    scored_df: pd.DataFrame,
    num_articles: int = 12,
    strategy: str = 'balanced'
) -> pd.DataFrame:
    """
    פונקציית עזר פשוטה לתכנון (תואמת את התוכנית המקורית)

    Args:
        scored_df: DataFrame עם ציונים ו-clusters
        num_articles: מספר מאמרים לחודש
        strategy: אסטרטגיה

    Returns:
        DataFrame עם התוכנית
    """
    planner = ContentPlanner()
    result = planner.generate_monthly_plan(
        scored_df,
        num_articles=num_articles,
        strategy=strategy
    )
    return result['plan']


def create_comprehensive_plan(
    df: pd.DataFrame,
    num_articles: int = 12,
    strategy: str = 'balanced',
    posts_per_week: int = 3
) -> Dict:
    """
    יצירת תוכנית מקיפה עם כל הפרטים

    Args:
        df: DataFrame עם נתונים מנוקים וציונים
        num_articles: מספר מאמרים
        strategy: אסטרטגיה
        posts_per_week: פוסטים בשבוע

    Returns:
        מילון עם תוכנית מקיפה
    """
    # צור תוכנית
    planner = ContentPlanner()
    plan_result = planner.generate_monthly_plan(
        df,
        num_articles=num_articles,
        strategy=strategy
    )

    plan_df = plan_result['plan']

    # הוסף לוח זמנים
    plan_with_schedule = planner.suggest_publishing_schedule(
        plan_df,
        posts_per_week=posts_per_week
    )

    # צור בריפים
    briefs = planner.create_content_briefs(plan_with_schedule)

    return {
        'plan': plan_with_schedule,
        'summary': plan_result['summary'],
        'cluster_distribution': plan_result['cluster_distribution'],
        'briefs': briefs
    }


if __name__ == "__main__":
    """
    בדיקה מהירה של המודול
    """
    print("=== בדיקת מנוע התכנון ===\n")

    # יצירת נתוני דוגמה
    sample_data = pd.DataFrame({
        'query': [
            'מדריך SEO מתחילים', 'SEO לאתרים', 'איך לעשות SEO',
            'שיווק דיגיטלי מתחילים', 'שיווק באינטרנט',
            'פרסום ממומן גוגל', 'פרסום פייסבוק',
            'כתיבת תוכן SEO', 'אופטימיזציה חיפוש'
        ],
        'impressions': [2000, 1500, 1800, 1200, 1000, 900, 800, 700, 1100],
        'clicks': [150, 120, 140, 90, 80, 70, 65, 60, 85],
        'ctr': [0.075, 0.08, 0.078, 0.075, 0.08, 0.078, 0.081, 0.086, 0.077],
        'position': [5.2, 6.1, 5.8, 8.3, 9.1, 11.2, 12.5, 7.4, 6.8],
        'opportunity_score': [85, 82, 83, 75, 72, 68, 65, 78, 80],
        'quick_wins_score': [20, 15, 18, 10, 8, 5, 3, 12, 16],
        'cluster_id': [0, 0, 0, 1, 1, 2, 2, 0, 0]
    })

    # צור תוכנית
    planner = ContentPlanner()
    result = planner.generate_monthly_plan(sample_data, num_articles=6)

    print("=== תוכנית תוכן חודשית ===")
    print(result['plan'][['query', 'content_type', 'opportunity_score', 'priority']].to_string())

    print("\n=== סיכום ===")
    for key, value in result['summary'].items():
        print(f"{key}: {value}")

    print("\n=== התפלגות לפי קלאסטרים ===")
    for cluster_id, count in result['cluster_distribution'].items():
        print(f"קלאסטר {cluster_id}: {count} מאמרים")

    # צור בריפים
    print("\n=== דוגמה לבריף ===")
    briefs = planner.create_content_briefs(result['plan'])
    print(f"\nבריף למאמר #{1}:")
    for key, value in briefs[0].items():
        print(f"  {key}: {value}")
