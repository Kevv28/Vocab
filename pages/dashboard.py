import streamlit as st
from utils.word_utils import (get_words, get_words_added_today, get_due_revisions,
                               get_streak, get_accuracy, get_learning_score, get_daily_stats)
from utils.note_utils import get_heatmap_data
from utils.ui_helpers import get_word_of_day, metric_card
from charts.charts import weekly_progress_chart, monthly_chart, heatmap_chart
from database.models import get_session, Word, Statistics
from datetime import date

def show_dashboard(user_id):
    st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)

    session = get_session()
    total_words = session.query(Word).filter(Word.user_id == user_id).count()
    session.close()

    today_count = get_words_added_today(user_id)
    due_count = len(get_due_revisions(user_id))
    streak = get_streak(user_id)
    accuracy = get_accuracy(user_id)
    learning_score = get_learning_score(user_id)
    stats = get_daily_stats(user_id, 30)
    active_days = len([s for s in stats if s.words_added > 0 or s.words_revised > 0])

    # Metrics row
    cols = st.columns(4)
    with cols[0]: metric_card("Total Words", total_words, color="#6C63FF")
    with cols[1]: metric_card("Added Today", today_count, color="#43D9A2")
    with cols[2]: metric_card("Due for Revision", due_count, color="#FF6584")
    with cols[3]: metric_card("Current Streak 🔥", f"{streak} days", color="#FFB347")

    cols2 = st.columns(4)
    with cols2[0]: metric_card("Accuracy", f"{accuracy}%", color="#43D9A2")
    with cols2[1]: metric_card("Days Studied", active_days, color="#6C63FF")
    with cols2[2]: metric_card("Learning Score", f"{learning_score}/100", color="#8B5CF6")
    with cols2[3]: metric_card("Revisions Done", sum(s.words_revised for s in stats), color="#FFB347")

    # Learning Score bar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🎯 Learning Score")
    st.progress(int(learning_score) / 100)
    st.markdown(f"<p style='color:#888;font-size:0.85rem'>Score: {learning_score}/100 — Keep studying daily to improve!</p>", unsafe_allow_html=True)

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 📈 Weekly Progress")
        fig = weekly_progress_chart(stats)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet. Start adding words!")

    with col_b:
        st.markdown("#### 📅 Monthly Trend")
        fig2 = monthly_chart(stats)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data yet.")

    # Heatmap
    st.markdown("#### 🗓️ Study Heatmap (GitHub-style)")
    hdata = get_heatmap_data(user_id)
    fig3 = heatmap_chart(hdata)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)

    # Word of the Day + Recent words
    col1, col2 = st.columns([1, 1])
    with col1:
        wod = get_word_of_day()
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#6C63FF22,#8B5CF622);border:1px solid #6C63FF44;
        border-radius:12px;padding:20px;'>
            <p style='color:#888;margin:0;font-size:0.8rem'>✨ WORD OF THE DAY</p>
            <h2 style='color:#6C63FF;margin:8px 0'>{wod['word']}</h2>
            <p style='color:#ccc'>{wod['meaning']}</p>
            <p style='color:#888;font-style:italic;font-size:0.9rem'>"{wod['example']}"</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🕐 Recently Added")
        recent = get_words(user_id, sort_by='date_added')[:5]
        if recent:
            for w in recent:
                st.markdown(f"""
                <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:8px;padding:10px;margin:4px 0'>
                    <span style='color:#6C63FF;font-weight:600'>{w.word}</span>
                    <span style='color:#888;font-size:0.85rem'> — {(w.meaning or '')[:60]}...</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No words yet. Add your first word!")

    # Due revisions alert
    if due_count > 0:
        st.warning(f"⚠️ You have **{due_count}** words due for revision! Go to the Revisions page.")
