import streamlit as st
from utils.note_utils import add_note, get_notes, get_note_by_date, delete_note
from utils.ui_helpers import save_uploaded_file, show_image_preview
from datetime import date

MOOD_ICONS = {1: "😞", 2: "😐", 3: "🙂", 4: "😊", 5: "🤩"}

def show_notes(user_id):
    st.markdown("<h1>📝 Daily Study Notes</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Add / Edit Note", "📚 View All Notes"])

    with tab1:
        note_date = st.date_input("Date", value=date.today())
        existing = get_note_by_date(user_id, note_date)

        if existing:
            st.info(f"📌 Editing existing note for {note_date.strftime('%d %b %Y')}")

        with st.form("note_form"):
            c1, c2 = st.columns(2)
            with c1:
                words_count = st.number_input("Words Learned Today",
                    min_value=0, max_value=500,
                    value=existing.words_learned if existing else 0)
                time_spent = st.number_input("Time Spent (minutes)",
                    min_value=0, max_value=600,
                    value=existing.time_spent if existing else 0)
                topic = st.text_input("Today's Topic",
                    value=existing.topic if existing else "",
                    placeholder="e.g. CAT Vocabulary, RC Passages, GRE Prep")
            with c2:
                mood = st.slider("Productivity Rating",
                    min_value=1, max_value=5,
                    value=existing.mood_rating if existing else 3)
                st.markdown(f"<p style='font-size:2rem'>{MOOD_ICONS.get(mood, '🙂')}</p>", unsafe_allow_html=True)
                img_file = st.file_uploader("Attach Screenshot/Image", type=['png','jpg','jpeg'])

            content = st.text_area("Study Notes",
                value=existing.content if existing else "",
                height=200,
                placeholder="""Today's study notes...
                
Example:
• Learned 20 CAT words from Word Power Made Easy
• Revised RC vocabulary sets 1-3
• Focused on psychology-themed passages
• Key words: ephemeral, perspicacious, loquacious""")

            submitted = st.form_submit_button("💾 Save Note", width='stretch')

        if submitted:
            img_path = save_uploaded_file(img_file) if img_file else (existing.image_path if existing else None)
            ok, msg = add_note(user_id, note_date, words_count, time_spent, topic, content, mood, img_path)
            if ok:
                st.success(f"✅ Note saved for {note_date.strftime('%d %b %Y')}!")
            else:
                st.error(msg)

    with tab2:
        search = st.text_input("🔍 Search notes", placeholder="Search by topic or content...")
        notes = get_notes(user_id, search=search or None)

        if not notes:
            st.info("No notes yet. Start journaling your daily study sessions!")
            return

        for note in notes:
            mood_icon = MOOD_ICONS.get(note.mood_rating, "🙂")
            with st.expander(
                f"{mood_icon} **{note.date.strftime('%d %b %Y')}** — {note.topic or 'General Study'} | {note.words_learned} words | {note.time_spent} min",
                expanded=False
            ):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**📅 Date:** {note.date.strftime('%A, %d %B %Y')}")
                    st.markdown(f"**📚 Words Learned:** {note.words_learned}")
                    st.markdown(f"**⏱️ Time Spent:** {note.time_spent} minutes")
                    if note.topic:
                        st.markdown(f"**🎯 Topic:** {note.topic}")
                    st.markdown(f"**Mood:** {mood_icon} {note.mood_rating}/5")
                    if note.content:
                        st.markdown("---")
                        st.markdown(note.content)
                with c2:
                    if note.image_path:
                        show_image_preview(note.image_path)

                if st.button("🗑️ Delete Note", key=f"del_note_{note.id}"):
                    delete_note(note.id)
                    st.rerun()
