import streamlit as st
from utils.quiz_utils import get_quiz_question, record_quiz_result, get_quiz_stats

QUIZ_TYPES = {
    "word_to_meaning": "Word → Meaning",
    "meaning_to_word": "Meaning → Word",
    "synonym": "Synonyms",
    "antonym": "Antonyms",
    "fill_blank": "Fill in the Blank",
}

def show_quiz(user_id):
    st.markdown("<h1>🧠 Quiz Mode</h1>", unsafe_allow_html=True)

    stats = get_quiz_stats(user_id)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Attempted", stats['total'])
    with c2:
        st.metric("Correct ✅", stats['correct'])
    with c3:
        st.metric("Wrong ❌", stats['wrong'])
    with c4:
        st.metric("Accuracy", f"{stats['accuracy']}%")

    st.markdown("---")
    quiz_type = st.selectbox("Quiz Type", list(QUIZ_TYPES.keys()),
                              format_func=lambda x: QUIZ_TYPES[x])

    if st.button("🎯 Start New Question", width='stretch'):
        q = get_quiz_question(user_id, quiz_type)
        if q is None:
            st.warning("You need at least 4 words to take a quiz. Add more words first!")
            return
        st.session_state['current_quiz'] = q
        st.session_state['quiz_answered'] = False
        st.session_state['quiz_result'] = None

    q = st.session_state.get('current_quiz')
    if not q:
        st.info("Click 'Start New Question' to begin a quiz!")
        return

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#6C63FF22,#8B5CF622);border:1px solid #6C63FF44;
    border-radius:12px;padding:24px;margin:16px 0'>
        <p style='color:#888;font-size:0.85rem;text-transform:uppercase'>Question</p>
        <h3 style='color:#e0e0ff'>{q['question']}</h3>
    </div>""", unsafe_allow_html=True)

    answered = st.session_state.get('quiz_answered', False)
    result = st.session_state.get('quiz_result')

    for i, choice in enumerate(q['choices']):
        if choice is None:
            continue
        display_text = str(choice)[:100] + ("..." if len(str(choice)) > 100 else "")

        if answered:
            if str(choice) == str(q['correct']):
                st.markdown(f"""
                <div style='background:#43D9A222;border:2px solid #43D9A2;border-radius:8px;padding:12px;margin:4px 0;color:#43D9A2;font-weight:600'>
                    ✅ {display_text}
                </div>""", unsafe_allow_html=True)
            elif result and str(choice) == result and str(choice) != str(q['correct']):
                st.markdown(f"""
                <div style='background:#FF658422;border:2px solid #FF6584;border-radius:8px;padding:12px;margin:4px 0;color:#FF6584'>
                    ❌ {display_text}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:8px;padding:12px;margin:4px 0;color:#888'>
                    {display_text}
                </div>""", unsafe_allow_html=True)
        else:
            if st.button(display_text, key=f"choice_{i}", width='stretch'):
                is_correct = str(choice) == str(q['correct'])
                record_quiz_result(user_id, q['word_id'], q['quiz_type'], is_correct)
                st.session_state['quiz_answered'] = True
                st.session_state['quiz_result'] = str(choice)
                st.rerun()

    if answered:
        if str(st.session_state.get('quiz_result')) == str(q['correct']):
            st.success("🎉 Correct! Well done!")
        else:
            st.error(f"❌ Wrong! The correct answer was: **{q['correct']}**")

        if st.button("➡️ Next Question", width='stretch'):
            next_q = get_quiz_question(user_id, quiz_type)
            if next_q:
                st.session_state['current_quiz'] = next_q
                st.session_state['quiz_answered'] = False
                st.session_state['quiz_result'] = None
                st.rerun()
            else:
                st.warning("No more questions!")
