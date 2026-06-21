import streamlit as st
from utils.word_utils import get_words, delete_word, toggle_favorite, update_word
from utils.ui_helpers import show_image_preview, difficulty_badge, save_uploaded_file

def show_vocabulary(user_id):
    st.markdown("<h1>📖 Vocabulary Database</h1>", unsafe_allow_html=True)

    # Filters
    with st.expander("🔍 Search & Filter", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1: search = st.text_input("Search", placeholder="Word, meaning, synonym...")
        with c2: diff = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
        with c3: src = st.selectbox("Source", ["All", "CAT", "GRE", "Newspaper", "Book", "RC", "Other"])
        with c4: sort = st.selectbox("Sort by", ["date_added", "word", "difficulty"])

    fav_only = st.checkbox("⭐ Show favorites only")
    words = get_words(user_id, search=search or None, difficulty=diff, source=src,
                      favorites_only=fav_only, sort_by=sort)

    st.markdown(f"<p style='color:#888'>Showing **{len(words)}** words</p>", unsafe_allow_html=True)

    if not words:
        st.info("No words found. Add some words first!")
        return

    for word in words:
        fav_icon = "⭐" if word.is_favorite else "☆"
        diff_badge = difficulty_badge(word.difficulty or "Medium")
        src_badge = f'<span class="badge badge-source">{word.source or "Other"}</span>'

        with st.expander(f"{fav_icon} **{word.word}** {diff_badge} {src_badge}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                if word.meaning:
                    st.markdown(f"**📌 Meaning:** {word.meaning}")
                if word.hindi_meaning:
                    st.markdown(f"**🇮🇳 Hindi:** {word.hindi_meaning}")
                if word.part_of_speech:
                    st.markdown(f"**🏷️ Part of Speech:** `{word.part_of_speech}`")
                if word.synonyms:
                    st.markdown(f"**🔗 Synonyms:** {word.synonyms}")
                if word.antonyms:
                    st.markdown(f"**↔️ Antonyms:** {word.antonyms}")
                if word.example_sentence:
                    st.markdown(f"**💬 Example:** *{word.example_sentence}*")
                if word.personal_notes:
                    st.markdown(f"**📓 Notes:** {word.personal_notes}")
                st.markdown(f"<p style='color:#555;font-size:0.8rem'>Added: {word.date_added.strftime('%d %b %Y') if word.date_added else 'N/A'} | Revised: {word.revision_count}x | Level: {word.revision_level}</p>", unsafe_allow_html=True)
            with c2:
                if word.image_path:
                    show_image_preview(word.image_path)

            # Actions
            act1, act2, act3 = st.columns(3)
            with act1:
                if st.button(f"{'⭐ Unfav' if word.is_favorite else '☆ Favorite'}", key=f"fav_{word.id}"):
                    toggle_favorite(word.id)
                    st.rerun()
            with act2:
                if st.button("✏️ Edit", key=f"edit_{word.id}"):
                    st.session_state[f"editing_{word.id}"] = True

            with act3:
                if st.button("🗑️ Delete", key=f"del_{word.id}"):
                    st.session_state[f"confirm_del_{word.id}"] = True

            if st.session_state.get(f"confirm_del_{word.id}"):
                st.warning("Are you sure?")
                y, n = st.columns(2)
                with y:
                    if st.button("Yes, delete", key=f"yes_{word.id}"):
                        delete_word(word.id)
                        st.session_state.pop(f"confirm_del_{word.id}", None)
                        st.rerun()
                with n:
                    if st.button("Cancel", key=f"no_{word.id}"):
                        st.session_state.pop(f"confirm_del_{word.id}", None)

            # Edit form
            if st.session_state.get(f"editing_{word.id}"):
                st.markdown("---")
                with st.form(f"edit_form_{word.id}"):
                    e1, e2 = st.columns(2)
                    with e1:
                        new_meaning = st.text_area("Meaning", value=word.meaning or "")
                        new_hindi = st.text_input("Hindi Meaning", value=word.hindi_meaning or "")
                        new_syn = st.text_input("Synonyms", value=word.synonyms or "")
                        new_ant = st.text_input("Antonyms", value=word.antonyms or "")
                    with e2:
                        new_pos = st.selectbox("Part of Speech", ["", "noun","verb","adjective","adverb","preposition","conjunction","interjection"],
                                               index=["","noun","verb","adjective","adverb","preposition","conjunction","interjection"].index(word.part_of_speech or ""))
                        new_diff = st.selectbox("Difficulty", ["Easy","Medium","Hard"],
                                                index=["Easy","Medium","Hard"].index(word.difficulty or "Medium"))
                        new_src = st.selectbox("Source", ["CAT","GRE","Newspaper","Book","RC","Other"],
                                               index=["CAT","GRE","Newspaper","Book","RC","Other"].index(word.source or "Other"))
                        new_ex = st.text_area("Example Sentence", value=word.example_sentence or "")
                    new_notes = st.text_area("Personal Notes", value=word.personal_notes or "")
                    img = st.file_uploader("Update Image", type=['png','jpg','jpeg'])
                    s1, s2 = st.columns(2)
                    with s1:
                        if st.form_submit_button("💾 Save Changes", width='stretch'):
                            img_path = save_uploaded_file(img) if img else word.image_path
                            ok, msg = update_word(word.id, {
                                'meaning': new_meaning, 'hindi_meaning': new_hindi,
                                'synonyms': new_syn, 'antonyms': new_ant,
                                'part_of_speech': new_pos, 'difficulty': new_diff,
                                'source': new_src, 'example_sentence': new_ex,
                                'personal_notes': new_notes, 'image_path': img_path
                            })
                            if ok:
                                st.success(msg)
                                st.session_state.pop(f"editing_{word.id}", None)
                                st.rerun()
                            else:
                                st.error(msg)
                    with s2:
                        if st.form_submit_button("Cancel", width='stretch'):
                            st.session_state.pop(f"editing_{word.id}", None)
                            st.rerun()
