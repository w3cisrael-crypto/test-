"""
Super Agent - מערכת תכנון תוכן
נקודת כניסה ראשית למערכת

שלב 1: בדיקת חיבור ל-GSC ומשיכת נתונים בסיסית
שלב 2: ניתוח והמלצות עם מנוע ניקוד
שלב 3: תכנון תוכן חודשי עם Clustering
"""
import argparse
from datetime import datetime, timedelta
from src.collectors import GSCConnector
from src.logic.scoring import OpportunityScorer, rank_opportunities, get_opportunity_insights
from src.logic.clustering import KeywordClusterer, analyze_clusters
from src.logic.planner import ContentPlanner, create_comprehensive_plan
from src.utils.data_cleaning import DataCleaner


def main():
    """
    פונקציה ראשית - שלבים 1-3
    """
    print("=" * 60)
    print("Super Agent - מערכת תכנון תוכן אוטומטית")
    print("=" * 60)
    print("שלב 1-3: איסוף, ניתוח ותכנון תוכן")
    print("=" * 60)
    print()

    # ארגומנטים מהשורת הפקודה
    parser = argparse.ArgumentParser(
        description='משיכת נתונים מ-Google Search Console'
    )
    parser.add_argument(
        '--site',
        type=str,
        help='כתובת האתר (לדוגמה: https://example.com)',
        required=False
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='מספר ימים אחורה (ברירת מחדל: 30)'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='שמירת הנתונים לקובץ CSV'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='הפעלת מנוע הניקוד והמלצות (שלב 2)'
    )
    parser.add_argument(
        '--brand',
        type=str,
        nargs='+',
        help='מילות מפתח של המותג לסינון (לדוגמה: "שם החברה" "המותג")'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='מספר ההזדמנויות המובילות להצגה (ברירת מחדל: 10)'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=50.0,
        help='ציון מינימלי להצגת הזדמנויות (ברירת מחדל: 50.0)'
    )
    parser.add_argument(
        '--plan',
        action='store_true',
        help='יצירת תוכנית תוכן חודשית (שלב 3)'
    )
    parser.add_argument(
        '--num-articles',
        type=int,
        default=12,
        help='מספר מאמרים לתוכנית החודשית (ברירת מחדל: 12)'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        default='balanced',
        choices=['balanced', 'pillar_focused', 'quick_wins'],
        help='אסטרטגיית תכנון: balanced (ברירת מחדל), pillar_focused, quick_wins'
    )
    parser.add_argument(
        '--posts-per-week',
        type=int,
        default=3,
        help='מספר פוסטים בשבוע ללוח הזמנים (ברירת מחדל: 3)'
    )

    args = parser.parse_args()

    # אם לא סופק אתר, בקש מהמשתמש
    if not args.site:
        print("אנא הזן את כתובת האתר שלך:")
        print("דוגמאות:")
        print("  - https://example.com")
        print("  - sc-domain:example.com")
        print()
        site_url = input("כתובת האתר: ").strip()

        if not site_url:
            print("✗ לא הוזנה כתובת אתר. יציאה...")
            return
    else:
        site_url = args.site

    # חישוב טווח תאריכים
    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=args.days + 3)).strftime('%Y-%m-%d')

    print(f"\nמשיכת נתונים עבור: {site_url}")
    print(f"טווח תאריכים: {start_date} עד {end_date}")
    print()

    # יצירת המחבר
    connector = GSCConnector()

    # חיבור ל-API
    if not connector.connect():
        print("\n✗ נכשל בחיבור ל-Google Search Console")
        print("\nוודא ש:")
        print("  1. קובץ service-account.json קיים בתיקיית הפרויקט")
        print("  2. ה-Service Account הוסף כמשתמש ב-Search Console")
        print("  3. Search Console API מופעל בפרויקט ב-Google Cloud")
        return

    # משיכת נתונים
    df = connector.fetch_data(site_url, start_date, end_date)

    if df.empty:
        print("\n✗ לא נמשכו נתונים. בדוק את כתובת האתר והתאריכים.")
        return

    # הצגת סיכום
    print("\n" + "=" * 60)
    print("סיכום הנתונים")
    print("=" * 60)
    print(f"סה\"כ שאילתות: {len(df)}")
    print(f"סה\"כ קליקים: {df['clicks'].sum():,.0f}")
    print(f"סה\"כ חשיפות: {df['impressions'].sum():,.0f}")
    print(f"CTR ממוצע: {df['ctr'].mean():.2%}")
    print(f"מיקום ממוצע: {df['position'].mean():.1f}")

    # הצגת 10 השאילתות המובילות
    print("\n" + "=" * 60)
    print("10 השאילתות המובילות (לפי קליקים)")
    print("=" * 60)
    top_queries = df.nlargest(10, 'clicks')
    for idx, row in top_queries.iterrows():
        print(f"\n{row['query']}")
        print(f"  קליקים: {row['clicks']:,.0f} | חשיפות: {row['impressions']:,.0f} | "
              f"CTR: {row['ctr']:.2%} | מיקום: {row['position']:.1f}")

    # שלב 2: ניתוח והמלצות
    if args.analyze:
        print("\n" + "=" * 60)
        print("שלב 2: ניתוח הזדמנויות")
        print("=" * 60)

        # ניקוי נתונים
        cleaner = DataCleaner(brand_keywords=args.brand)
        df_clean = cleaner.clean_pipeline(
            df,
            remove_brand=bool(args.brand),
            min_impressions=10
        )

        if df_clean.empty:
            print("\n✗ לא נותרו נתונים לאחר הניקוי")
            return

        # חישוב ציונים
        print("\nמחשב ציוני הזדמנות...")
        scorer = OpportunityScorer()
        df_scored = scorer.score_dataframe(df_clean)

        # דירוג
        df_ranked = rank_opportunities(
            df_scored,
            top_n=args.top,
            min_score=args.min_score
        )

        # הצגת תובנות
        insights = get_opportunity_insights(df_scored)

        print("\n" + "=" * 60)
        print("תובנות כלליות")
        print("=" * 60)
        print(f"סה\"כ הזדמנויות: {insights.get('total_opportunities', 0)}")
        print(f"ציון ממוצע: {insights.get('avg_score', 0):.1f}")
        print(f"הזדמנויות גבוהות (75+): {insights.get('high_opportunities', 0)}")
        print(f"הזדמנויות בינוניות (50-75): {insights.get('medium_opportunities', 0)}")
        print(f"Quick Wins (שיפור CTR): {insights.get('quick_wins', 0)}")
        print(f"מילות מפתח בעמוד 2: {insights.get('page_2_keywords', 0)}")

        # הצגת ההזדמנויות המובילות
        print("\n" + "=" * 60)
        print(f"Top {len(df_ranked)} הזדמנויות (ציון {args.min_score}+)")
        print("=" * 60)

        for idx, row in df_ranked.iterrows():
            print(f"\n🎯 #{idx+1}: {row['query']}")
            print(f"   ציון כולל: {row['opportunity_score']:.1f}/100")
            print(f"   מיקום: {row['position']:.1f} | "
                  f"חשיפות: {row['impressions']:,.0f} | "
                  f"קליקים: {row['clicks']:,.0f} | "
                  f"CTR: {row['ctr']:.2%}")

            # פירוט רכיבי הציון
            print(f"   📊 פירוט: טראפיק={row['traffic_score']:.0f} | "
                  f"מיקום={row['position_score']:.0f} | "
                  f"Quick Win={row['quick_wins_score']:.0f}")

            # המלצה
            if row['quick_wins_score'] > 50:
                print(f"   💡 המלצה: שפר כותרת ו-meta description לשיפור CTR")
            elif row['position'] <= 10:
                print(f"   💡 המלצה: הוסף תוכן איכותי ושפר את הדף הקיים")
            elif row['position'] <= 20:
                print(f"   💡 המלצה: צור תוכן מקיף חדש כדי להגיע לעמוד 1")
            else:
                print(f"   💡 המלצה: צור Pillar content ותוכן תומך")

        # שמירת הנתונים המנותחים
        if args.save and not args.plan:
            print("\n" + "=" * 60)
            # שמור את הנתונים המנותחים
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analyzed_filename = f"analyzed_opportunities_{timestamp}.csv"

            from config.settings import PROCESSED_DATA_DIR
            filepath = PROCESSED_DATA_DIR / analyzed_filename

            df_ranked.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✓ הזדמנויות מנותחות נשמרו: {filepath}")

        # שלב 3: תכנון תוכן חודשי
        if args.plan:
            print("\n" + "=" * 60)
            print("שלב 3: תכנון תוכן חודשי")
            print("=" * 60)

            # קיבוץ מילות מפתח
            print("\nמקבץ מילות מפתח לנושאים...")
            clusterer = KeywordClusterer(language='hebrew')
            df_clustered = clusterer.cluster_keywords(df_scored)

            # ניתוח קלאסטרים
            cluster_analysis = analyze_clusters(df_clustered)

            print(f"✓ נוצרו {cluster_analysis.get('num_clusters', 0)} קלאסטרים")
            print(f"  ממוצע מילות מפתח בקלאסטר: {cluster_analysis.get('avg_keywords_per_cluster', 0):.1f}")

            # הצג נושאי קלאסטרים
            print("\n📋 נושאי קלאסטרים:")
            for cluster_id in sorted(df_clustered['cluster_id'].unique()):
                topic = clusterer.suggest_cluster_topic(df_clustered, cluster_id)
                count = len(df_clustered[df_clustered['cluster_id'] == cluster_id])
                print(f"  קלאסטר {cluster_id}: {topic} ({count} מילות מפתח)")

            # יצירת תוכנית
            print(f"\nבונה תוכנית תוכן עם {args.num_articles} מאמרים...")
            print(f"אסטרטגיה: {args.strategy}")

            plan_result = create_comprehensive_plan(
                df_clustered,
                num_articles=args.num_articles,
                strategy=args.strategy,
                posts_per_week=args.posts_per_week
            )

            plan_df = plan_result['plan']
            summary = plan_result['summary']
            briefs = plan_result['briefs']

            # הצגת סיכום
            print("\n" + "=" * 60)
            print("סיכום התוכנית")
            print("=" * 60)
            print(f"סה\"כ מאמרים: {summary['total_articles']}")
            print(f"  • Pillar (מאמרי עומק): {summary['pillar_articles']}")
            print(f"  • Cluster (מאמרים תומכים): {summary['cluster_articles']}")
            print(f"ציון הזדמנות ממוצע: {summary['avg_opportunity_score']:.1f}")
            print(f"פוטנציאל חשיפות: {summary['total_potential_impressions']:,.0f}")
            print(f"פוטנציאל קליקים: {summary['total_potential_clicks']:,.0f}")

            # הצגת התוכנית
            print("\n" + "=" * 60)
            print("תוכנית תוכן חודשית")
            print("=" * 60)

            for idx, row in plan_df.iterrows():
                week = row.get('week', '?')
                date = row.get('suggested_date', '').strftime('%d/%m') if 'suggested_date' in row else '?'
                priority = row.get('priority', idx + 1)
                content_type = row['content_type']

                # אייקון לפי סוג
                icon = "📌" if content_type == "Pillar" else "📄"

                print(f"\n{icon} שבוע {week} ({date}) - {content_type}")
                print(f"   מילת מפתח: {row['query']}")
                print(f"   ציון: {row['opportunity_score']:.1f} | מיקום: {row['position']:.1f} | "
                      f"חשיפות: {row['impressions']:,.0f}")

                # מצא את הבריף המתאים
                brief = briefs[idx] if idx < len(briefs) else {}
                if brief:
                    print(f"   אורך מומלץ: {brief.get('recommended_length', 'N/A')}")
                    print(f"   פעולה: {brief.get('action', 'N/A')}")

            # שמירת התוכנית
            if args.save:
                print("\n" + "=" * 60)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                plan_filename = f"content_plan_{timestamp}.csv"

                from config.settings import PROCESSED_DATA_DIR
                filepath = PROCESSED_DATA_DIR / plan_filename

                plan_df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"✓ תוכנית תוכן נשמרה: {filepath}")

                # שמור גם את הבריפים
                import json
                briefs_filename = f"content_briefs_{timestamp}.json"
                briefs_filepath = PROCESSED_DATA_DIR / briefs_filename

                with open(briefs_filepath, 'w', encoding='utf-8') as f:
                    json.dump(briefs, f, ensure_ascii=False, indent=2)

                print(f"✓ בריפים נשמרו: {briefs_filepath}")

    # שמירה לקובץ (נתונים גולמיים)
    elif args.save:
        print("\n" + "=" * 60)
        filepath = connector.save_data(df)
        if filepath:
            print(f"✓ הנתונים נשמרו בהצלחה: {filepath}")

    print("\n" + "=" * 60)
    print("✓ השלמה בהצלחה!")
    print("=" * 60)

    if not args.analyze:
        print("\n💡 טיפ: הוסף --analyze כדי לקבל ניתוח מעמיק והמלצות!")

    if args.analyze and not args.plan:
        print("💡 טיפ: הוסף --plan ליצירת תוכנית תוכן חודשית מלאה!")


if __name__ == "__main__":
    main()
