"""
Super Agent - Dashboard
ממשק גרפי למערכת תכנון תוכן

הרצה:
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

from src.collectors import GSCConnector
from src.logic import (
    OpportunityScorer,
    rank_opportunities,
    get_opportunity_insights,
    KeywordClusterer,
    analyze_clusters,
    create_comprehensive_plan
)
from src.utils import DataCleaner


# הגדרות עמוד
st.set_page_config(
    page_title="Super Agent - תכנון תוכן",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם אישית
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .pillar-badge {
        background-color: #ff7f0e;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .cluster-badge {
        background-color: #2ca02c;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """אתחול Session State"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df_raw' not in st.session_state:
        st.session_state.df_raw = None
    if 'df_scored' not in st.session_state:
        st.session_state.df_scored = None
    if 'df_clustered' not in st.session_state:
        st.session_state.df_clustered = None
    if 'plan_result' not in st.session_state:
        st.session_state.plan_result = None


def load_data(site_url: str, days: int, brand_keywords: list) -> tuple:
    """טעינת נתונים מ-GSC וניתוח"""
    with st.spinner('🔄 מתחבר ל-Google Search Console...'):
        connector = GSCConnector()
        if not connector.connect():
            st.error("❌ נכשל בחיבור ל-GSC. בדוק את קובץ ה-credentials.")
            return None, None, None

    # חישוב תאריכים
    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days + 3)).strftime('%Y-%m-%d')

    with st.spinner(f'📥 מושך נתונים מ-{start_date} עד {end_date}...'):
        df = connector.fetch_data(site_url, start_date, end_date)

    if df.empty:
        st.error("❌ לא נמצאו נתונים לתקופה המבוקשת.")
        return None, None, None

    # ניקוי
    with st.spinner('🧹 מנקה ומעבד נתונים...'):
        cleaner = DataCleaner(brand_keywords=brand_keywords)
        df_clean = cleaner.clean_pipeline(
            df,
            remove_brand=bool(brand_keywords),
            min_impressions=10
        )

    if df_clean.empty:
        st.error("❌ לא נותרו נתונים לאחר הניקוי.")
        return None, None, None

    # ניקוד
    with st.spinner('🎯 מחשב ציוני הזדמנות...'):
        scorer = OpportunityScorer()
        df_scored = scorer.score_dataframe(df_clean)

    # קיבוץ
    with st.spinner('🔗 מקבץ מילות מפתח...'):
        clusterer = KeywordClusterer(language='hebrew')
        df_clustered = clusterer.cluster_keywords(df_scored)

    st.success('✅ הנתונים נטענו בהצלחה!')

    return df, df_scored, df_clustered


def display_overview(df_scored: pd.DataFrame):
    """הצגת סקירה כללית"""
    st.markdown("## 📊 סקירה כללית")

    insights = get_opportunity_insights(df_scored)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "סה\"כ הזדמנויות",
            f"{insights.get('total_opportunities', 0):,}",
            help="מספר מילות מפתח שנמצאו"
        )

    with col2:
        st.metric(
            "ציון ממוצע",
            f"{insights.get('avg_score', 0):.1f}",
            help="ציון הזדמנות ממוצע"
        )

    with col3:
        st.metric(
            "הזדמנויות גבוהות",
            insights.get('high_opportunities', 0),
            help="מילות מפתח עם ציון 75+"
        )

    with col4:
        st.metric(
            "Quick Wins",
            insights.get('quick_wins', 0),
            help="הזדמנויות לשיפור CTR"
        )

    # גרף התפלגות ציונים
    st.markdown("### התפלגות ציוני הזדמנות")

    fig = px.histogram(
        df_scored,
        x='opportunity_score',
        nbins=20,
        title='',
        labels={'opportunity_score': 'ציון הזדמנות', 'count': 'מספר מילות מפתח'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def display_top_opportunities(df_scored: pd.DataFrame, top_n: int = 10):
    """הצגת הזדמנויות מובילות"""
    st.markdown(f"## 🎯 Top {top_n} הזדמנויות")

    df_top = df_scored.nlargest(top_n, 'opportunity_score')

    for idx, row in df_top.iterrows():
        with st.expander(f"#{idx+1} - {row['query']} (ציון: {row['opportunity_score']:.1f})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**מיקום נוכחי:** {row['position']:.1f}")
                st.markdown(f"**חשיפות חודשיות:** {row['impressions']:,}")
                st.markdown(f"**קליקים חודשיים:** {row['clicks']:,}")
                st.markdown(f"**CTR:** {row['ctr']:.2%}")

            with col2:
                st.markdown("**פירוט ציון:**")
                st.progress(row['traffic_score'] / 100)
                st.caption(f"טראפיק: {row['traffic_score']:.0f}")

                st.progress(row['position_score'] / 100)
                st.caption(f"מיקום: {row['position_score']:.0f}")

                st.progress(row['quick_wins_score'] / 100)
                st.caption(f"Quick Win: {row['quick_wins_score']:.0f}")

            # המלצה
            if row['quick_wins_score'] > 50:
                st.info("💡 **המלצה:** שפר כותרת ו-meta description לשיפור CTR")
            elif row['position'] <= 10:
                st.info("💡 **המלצה:** הוסף תוכן איכותי ושפר את הדף הקיים")
            elif row['position'] <= 20:
                st.info("💡 **המלצה:** צור תוכן מקיף חדש כדי להגיע לעמוד 1")
            else:
                st.info("💡 **המלצה:** צור Pillar content ותוכן תומך")


def display_clusters(df_clustered: pd.DataFrame):
    """הצגת קלאסטרים"""
    st.markdown("## 🔗 קלאסטרים ונושאים")

    analysis = analyze_clusters(df_clustered)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("מספר קלאסטרים", analysis.get('num_clusters', 0))

    with col2:
        st.metric(
            "ממוצע מילות מפתח",
            f"{analysis.get('avg_keywords_per_cluster', 0):.1f}"
        )

    with col3:
        st.metric(
            "קלאסטר הכי גדול",
            analysis.get('largest_cluster_size', 0)
        )

    # טבלת קלאסטרים
    clusterer = KeywordClusterer()
    summary = clusterer.get_cluster_summary(df_clustered)

    st.markdown("### פירוט קלאסטרים")

    for cluster_id in sorted(df_clustered['cluster_id'].unique()):
        topic = clusterer.suggest_cluster_topic(df_clustered, cluster_id)
        cluster_data = df_clustered[df_clustered['cluster_id'] == cluster_id]

        with st.expander(f"🏷️ קלאסטר {cluster_id}: {topic} ({len(cluster_data)} מילות מפתח)"):
            st.dataframe(
                cluster_data[['query', 'opportunity_score', 'position', 'impressions']].head(10),
                use_container_width=True
            )


def display_content_plan(plan_result: dict):
    """הצגת תוכנית תוכן"""
    st.markdown("## 📅 תוכנית תוכן חודשית")

    plan_df = plan_result['plan']
    summary = plan_result['summary']
    briefs = plan_result['briefs']

    # סיכום
    st.markdown("### סיכום התוכנית")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("סה\"כ מאמרים", summary['total_articles'])

    with col2:
        st.metric(
            "📌 Pillar",
            summary['pillar_articles'],
            help="מאמרי עומק מקיפים"
        )

    with col3:
        st.metric(
            "📄 Cluster",
            summary['cluster_articles'],
            help="מאמרים תומכים"
        )

    with col4:
        st.metric(
            "ציון ממוצע",
            f"{summary['avg_opportunity_score']:.1f}"
        )

    # גרף התפלגות לפי סוג
    fig = px.pie(
        plan_df,
        names='content_type',
        title='התפלגות סוגי תוכן',
        color='content_type',
        color_discrete_map={'Pillar': '#ff7f0e', 'Cluster': '#2ca02c'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # תוכנית מפורטת
    st.markdown("### תוכנית מפורטת")

    for idx, row in plan_df.iterrows():
        content_type = row['content_type']
        icon = "📌" if content_type == "Pillar" else "📄"
        badge_class = "pillar-badge" if content_type == "Pillar" else "cluster-badge"

        week = row.get('week', '?')
        date = row.get('suggested_date', '').strftime('%d/%m/%Y') if 'suggested_date' in row else '?'

        with st.expander(f"{icon} שבוע {week} ({date}) - {row['query']}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"<span class='{badge_class}'>{content_type}</span>", unsafe_allow_html=True)
                st.markdown(f"**מילת מפתח:** {row['query']}")
                st.markdown(f"**ציון:** {row['opportunity_score']:.1f}/100")
                st.markdown(f"**מיקום נוכחי:** {row['position']:.1f}")
                st.markdown(f"**חשיפות:** {row['impressions']:,}")

            with col2:
                brief = briefs[idx] if idx < len(briefs) else {}
                if brief:
                    st.markdown("**המלצות:**")
                    st.info(f"📏 אורך: {brief.get('recommended_length', 'N/A')}")
                    st.info(f"🎯 פעולה: {brief.get('action', 'N/A')}")

    # כפתור הורדה
    st.markdown("### 💾 ייצוא")

    col1, col2 = st.columns(2)

    with col1:
        csv = plan_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 הורד תוכנית (CSV)",
            data=csv,
            file_name=f"content_plan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col2:
        json_str = json.dumps(briefs, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 הורד בריפים (JSON)",
            data=json_str,
            file_name=f"content_briefs_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )


def main():
    """פונקציה ראשית"""
    init_session_state()

    # Header
    st.markdown('<h1 class="main-header">📊 Super Agent - מערכת תכנון תוכן</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ הגדרות")

        site_url = st.text_input(
            "כתובת אתר",
            placeholder="https://example.com",
            help="כתובת האתר ב-Search Console"
        )

        days = st.slider(
            "תקופת נתונים (ימים)",
            min_value=7,
            max_value=90,
            value=30,
            help="כמה ימים אחורה למשוך נתונים"
        )

        brand_keywords = st.text_input(
            "מילות מותג (הפרד בפסיקים)",
            placeholder="שם החברה, המותג",
            help="מילות מפתח של המותג לסינון"
        )

        brand_list = [kw.strip() for kw in brand_keywords.split(',')] if brand_keywords else []

        st.markdown("---")

        st.markdown("## 📋 תכנון")

        num_articles = st.number_input(
            "מספר מאמרים",
            min_value=1,
            max_value=50,
            value=12,
            help="כמה מאמרים לתכנן"
        )

        strategy = st.selectbox(
            "אסטרטגיה",
            options=['balanced', 'pillar_focused', 'quick_wins'],
            format_func=lambda x: {
                'balanced': '⚖️ מאוזן',
                'pillar_focused': '📌 דגש על Pillar',
                'quick_wins': '⚡ Quick Wins'
            }[x],
            help="אסטרטגיית התכנון"
        )

        posts_per_week = st.slider(
            "פוסטים בשבוע",
            min_value=1,
            max_value=7,
            value=3
        )

        st.markdown("---")

        load_button = st.button("🚀 טען נתונים", type="primary", use_container_width=True)

    # טעינת נתונים
    if load_button:
        if not site_url:
            st.error("❌ אנא הזן כתובת אתר")
        else:
            df_raw, df_scored, df_clustered = load_data(site_url, days, brand_list)

            if df_scored is not None:
                st.session_state.data_loaded = True
                st.session_state.df_raw = df_raw
                st.session_state.df_scored = df_scored
                st.session_state.df_clustered = df_clustered

    # הצגת תוצאות
    if st.session_state.data_loaded:
        tabs = st.tabs(["📊 סקירה", "🎯 הזדמנויות", "🔗 קלאסטרים", "📅 תוכנית"])

        with tabs[0]:
            display_overview(st.session_state.df_scored)

        with tabs[1]:
            display_top_opportunities(st.session_state.df_scored, top_n=15)

        with tabs[2]:
            display_clusters(st.session_state.df_clustered)

        with tabs[3]:
            if st.button("📝 צור תוכנית תוכן", type="primary"):
                with st.spinner('🎨 יוצר תוכנית...'):
                    plan_result = create_comprehensive_plan(
                        st.session_state.df_clustered,
                        num_articles=num_articles,
                        strategy=strategy,
                        posts_per_week=posts_per_week
                    )
                    st.session_state.plan_result = plan_result

            if st.session_state.plan_result:
                display_content_plan(st.session_state.plan_result)

    else:
        st.info("👈 הזן את פרטי האתר בסרגל הצד והקלק על 'טען נתונים' להתחלה")

        # הצגת דוגמה
        with st.expander("💡 איך זה עובד?"):
            st.markdown("""
            ### תהליך העבודה:

            1. **הזן כתובת אתר** מ-Google Search Console
            2. **בחר תקופת נתונים** (מומלץ 30-90 ימים)
            3. **הוסף מילות מותג** (אופציונלי) לסינון
            4. **הקלק על 'טען נתונים'** - המערכת תעשה:
               - משיכת נתונים מ-GSC
               - ניקוי וסינון
               - חישוב ציוני הזדמנות
               - קיבוץ מילות מפתח
            5. **עבור בין הטאבים** לניתוח
            6. **צור תוכנית תוכן** מותאמת אישית
            7. **הורד את התוכנית** ל-CSV או JSON

            ### דרישות:
            - קובץ `service-account.json` בתיקיית הפרויקט
            - גישה ל-Search Console API
            """)


if __name__ == "__main__":
    main()
