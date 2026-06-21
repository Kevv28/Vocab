import streamlit as st
from utils.word_utils import get_due_revisions, mark_revised, get_words
from database.models import get_session, Word
from datetime import datetime, timedelta

INTERVALS = {0: 1, 1: 3, 2: 7, 3: 15, 4: 30}

def show_revisions(user_id):
    st.markdown("<h1>🔄 Spaced Repetition Revisions</h1>", unsafe_allow_html=True)

    # SRS explanation
    cols = st.columns(5)
    level_info = [(1, "1 day"), (2, "3 days"), (3, "7 days"), (4, "15 days"), (5, "30 days")]
    for col, (lv, days) in zip(cols, level_info):
        with col:
            st.markdown(f"""
            <div style='background:#2a2a3e;border:1px solid #6C63FF44;border-radius:8px;padding:10px;text-align:center'>
                <p style='color:#6C63FF;font-size:1.2rem;margin:0'>L{lv}</p>
                <p style='color:#888;font-size:0.8rem;margin:0'>{days}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Due words
    due = get_due_revisions(user_id)

    tab1, tab2, tab3 = st.tabs([f"🔴 Due Now ({len(due)})", "📅 Upcoming", "📊 All Words"])

    with tab1:
        if not due:
            st.success("🎉 No words due for revision right now! Great job staying on top of it.")
        else:
            st.info(f"**{len(due)} words** need revision. Review each word and mark it as revised.")
            for word in due:
                overdue_days = 0
                if word.next_revision:
                    overdue_days = max(0, (datetime.utcnow() - word.next_revision).days)
                overdue_label = f" ⚠️ {overdue_days}d overdue" if overdue_days > 0 else ""

                with st.expander(f"**{word.word}**{overdue_label} — Level {word.revision_level}", expanded=False):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        if word.meaning:
                            st.markdown(f"**Meaning:** {word.meaning}")
                        if word.hindi_meaning:
                            st.markdown(f"**Hindi:** {word.hindi_meaning}")
                        if word.synonyms:
                            st.markdown(f"**Synonyms:** {word.synonyms}")
                        if word.antonyms:
                            st.markdown(f"**Antonyms:** {word.antonyms}")
                        if word.example_sentence:
                            st.markdown(f"**Example:** *{word.example_sentence}*")
                        next_level = min(word.revision_level + 1, 4)
                        next_interval = INTERVALS[next_level]
                        st.markdown(f"<p style='color:#888;font-size:0.8rem'>Next revision after marking: {next_interval} days | Revised {word.revision_count} times</p>", unsafe_allow_html=True)
                    with c2:
                        if st.button("✅ Mark Revised", key=f"rev_{word.id}", width='stretch'):
                            mark_revised(word.id, user_id)
                            st.success(f"'{word.word}' revised!")
                            st.rerun()

    with tab2:
        session = get_session()
        upcoming = session.query(Word).filter(
            Word.user_id == user_id,
            Word.next_revision > datetime.utcnow()
        ).order_by(Word.next_revision).limit(20).all()
        session.close()

        if upcoming:
            for w in upcoming:
                days_until = max(0, (w.next_revision - datetime.utcnow()).days) if w.next_revision else 0
                st.markdown(f"""
                <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:8px;padding:12px;margin:4px 0;
                display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <span style='color:#6C63FF;font-weight:600'>{w.word}</span>
                        <span style='color:#888;font-size:0.85rem'> — {(w.meaning or '')[:50]}</span>
                    </div>
                    <span style='color:#43D9A2;font-size:0.85rem'>In {days_until}d (L{w.revision_level})</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No upcoming revisions scheduled.")

    with tab3:
        words = get_words(user_id, sort_by='word')
        if words:
            for w in words:
                level_color = ['#888', '#43D9A2', '#6C63FF', '#FFB347', '#FF6584', '#FF6584'][min(w.revision_level, 5)]
                st.markdown(f"""
                <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:8px;padding:10px;margin:3px 0'>
                    <span style='color:#e0e0ff;font-weight:600'>{w.word}</span>
                    <span style='background:{level_color}22;color:{level_color};padding:2px 8px;border-radius:20px;font-size:0.75rem;margin-left:8px'>L{w.revision_level}</span>
                    <span style='color:#888;font-size:0.8rem;margin-left:8px'>Revised {w.revision_count}x</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Add some words to see them here.")

    # Random revision button
    st.markdown("---")
    st.markdown("#### 🎲 Random Revision")
    if st.button("Pick a Random Word to Revise", width='stretch'):
        import random
        all_words = get_words(user_id)
        if all_words:
            pick = random.choice(all_words)
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#6C63FF22,#8B5CF622);border:1px solid #6C63FF44;
            border-radius:12px;padding:20px;margin-top:12px'>
                <h2 style='color:#6C63FF'>{pick.word}</h2>
                <p style='color:#ccc'><b>Meaning:</b> {pick.meaning}</p>
                {'<p style="color:#888"><b>Hindi:</b> '+pick.hindi_meaning+'</p>' if pick.hindi_meaning else ''}
                {'<p style="color:#888"><b>Synonyms:</b> '+pick.synonyms+'</p>' if pick.synonyms else ''}
                {'<p style="color:#888;font-style:italic">"'+pick.example_sentence+'"</p>' if pick.example_sentence else ''}
            </div>""", unsafe_allow_html=True)
