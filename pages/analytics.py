import streamlit as st
from utils.word_utils import get_words, get_daily_stats, get_streak, get_accuracy, get_learning_score
from utils.quiz_utils import get_quiz_stats
from charts.charts import (weekly_progress_chart, monthly_chart, difficulty_pie,
                            streak_chart, source_bar)
from database.models import get_session, Word, Statistics

def show_analytics(user_id):
    st.markdown("<h1>📊 Analytics Dashboard</h1>", unsafe_allow_html=True)

    words = get_words(user_id)
    stats = get_daily_stats(user_id, 30)
    quiz_stats = get_quiz_stats(user_id)
    streak = get_streak(user_id)
    accuracy = get_accuracy(user_id)
    score = get_learning_score(user_id)

    # Summary metrics
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Words", len(words))
    c2.metric("Current Streak", f"{streak}🔥")
    c3.metric("Accuracy", f"{accuracy}%")
    c4.metric("Quiz Attempted", quiz_stats['total'])
    c5.metric("Learning Score", f"{score}/100")

    st.markdown("---")

    # Charts row 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📈 Weekly Progress")
        fig = weekly_progress_chart(stats)
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("No data yet.")

    with col2:
        st.markdown("#### 📅 Monthly Learning Trend")
        fig2 = monthly_chart(stats)
        if fig2: st.plotly_chart(fig2, use_container_width=True)
        else: st.info("No data yet.")

    # Charts row 2
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🥧 Difficulty Distribution")
        fig3 = difficulty_pie(words)
        if fig3: st.plotly_chart(fig3, use_container_width=True)
        else: st.info("No words yet.")

    with col4:
        st.markdown("#### 📚 Words by Source")
        fig4 = source_bar(words)
        if fig4: st.plotly_chart(fig4, use_container_width=True)
        else: st.info("No words yet.")

    # Streak chart full width
    st.markdown("#### 🔥 Study Activity (Last 30 Days)")
    fig5 = streak_chart(stats)
    if fig5: st.plotly_chart(fig5, use_container_width=True)

    # Quiz breakdown
    st.markdown("---")
    st.markdown("#### 🧠 Quiz Performance")
    if quiz_stats['total'] > 0:
        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            st.markdown(f"""
            <div style='background:#43D9A222;border:1px solid #43D9A255;border-radius:10px;padding:16px;text-align:center'>
                <p style='color:#888;margin:0'>Correct</p>
                <h2 style='color:#43D9A2'>{quiz_stats['correct']}</h2>
            </div>""", unsafe_allow_html=True)
        with qc2:
            st.markdown(f"""
            <div style='background:#FF658422;border:1px solid #FF658455;border-radius:10px;padding:16px;text-align:center'>
                <p style='color:#888;margin:0'>Wrong</p>
                <h2 style='color:#FF6584'>{quiz_stats['wrong']}</h2>
            </div>""", unsafe_allow_html=True)
        with qc3:
            st.markdown(f"""
            <div style='background:#6C63FF22;border:1px solid #6C63FF55;border-radius:10px;padding:16px;text-align:center'>
                <p style='color:#888;margin:0'>Accuracy</p>
                <h2 style='color:#6C63FF'>{quiz_stats['accuracy']}%</h2>
            </div>""", unsafe_allow_html=True)
        st.progress(int(quiz_stats['accuracy']) / 100)
    else:
        st.info("No quiz data yet. Take some quizzes first!")

    # Words needing attention
    st.markdown("---")
    st.markdown("#### ⚠️ Words Needing Attention (Most Wrong Answers)")
    hard_words = sorted(words, key=lambda w: w.wrong_count, reverse=True)[:10]
    hard_words = [w for w in hard_words if w.wrong_count > 0]
    if hard_words:
        for w in hard_words:
            total = w.correct_count + w.wrong_count
            acc = round(w.correct_count / total * 100) if total else 0
            color = "#43D9A2" if acc >= 70 else "#FFB347" if acc >= 40 else "#FF6584"
            st.markdown(f"""
            <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:8px;padding:10px;margin:4px 0;
            display:flex;justify-content:space-between;align-items:center'>
                <div>
                    <span style='color:#e0e0ff;font-weight:600'>{w.word}</span>
                    <span style='color:#888;font-size:0.85rem'> — {(w.meaning or '')[:50]}</span>
                </div>
                <span style='color:{color};font-size:0.85rem'>{acc}% ({w.correct_count}✅ {w.wrong_count}❌)</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No quiz attempts yet. Take a quiz to see weak words.")

    # Revision completion rate
    from utils.word_utils import get_due_revisions
    due = get_due_revisions(user_id)
    total_w = len(words)
    if total_w > 0:
        completion = max(0, round((1 - len(due)/total_w) * 100))
        st.markdown("---")
        st.markdown(f"#### ✅ Revision Completion Rate: {completion}%")
        st.progress(completion / 100)
