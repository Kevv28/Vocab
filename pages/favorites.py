import streamlit as st
from utils.word_utils import get_words, toggle_favorite
from utils.ui_helpers import difficulty_badge, show_image_preview

def show_favorites(user_id):
    st.markdown("<h1>⭐ Favorite Words</h1>", unsafe_allow_html=True)

    words = get_words(user_id, favorites_only=True)
    if not words:
        st.info("No favorite words yet. Star words from the Vocabulary page to see them here!")
        return

    st.markdown(f"<p style='color:#888'>You have **{len(words)}** favorite words.</p>", unsafe_allow_html=True)

    search = st.text_input("🔍 Filter favorites", placeholder="Search your favorites...")
    if search:
        words = [w for w in words if search.lower() in w.word.lower() or search.lower() in (w.meaning or '').lower()]

    for word in words:
        diff_badge = difficulty_badge(word.difficulty or "Medium")
        src_badge = f'<span class="badge badge-source">{word.source or "Other"}</span>'
        with st.expander(f"⭐ **{word.word}** {diff_badge} {src_badge}", expanded=False):
            c1, c2 = st.columns([3,1])
            with c1:
                if word.meaning:      st.markdown(f"**📌 Meaning:** {word.meaning}")
                if word.hindi_meaning: st.markdown(f"**🇮🇳 Hindi:** {word.hindi_meaning}")
                if word.synonyms:     st.markdown(f"**🔗 Synonyms:** {word.synonyms}")
                if word.antonyms:     st.markdown(f"**↔️ Antonyms:** {word.antonyms}")
                if word.example_sentence: st.markdown(f"**💬 Example:** *{word.example_sentence}*")
                if word.personal_notes:   st.markdown(f"**📓 Notes:** {word.personal_notes}")
            with c2:
                if word.image_path: show_image_preview(word.image_path)

            if st.button("☆ Remove from Favorites", key=f"unfav_{word.id}"):
                toggle_favorite(word.id)
                st.rerun()

    # Flash card mode
    st.markdown("---")
    st.markdown("#### 🎴 Flash Card Mode")
    if st.button("🔀 Show Random Favorite Word"):
        import random
        pick = random.choice(words)
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#FFB34722,#FF658422);border:1px solid #FFB34755;
        border-radius:12px;padding:24px;margin-top:12px;text-align:center'>
            <p style='color:#888;font-size:0.85rem;margin:0'>⭐ FAVORITE WORD</p>
            <h1 style='color:#FFB347;margin:12px 0'>{pick.word}</h1>
            <p style='color:#ccc;font-size:1.1rem'>{pick.meaning}</p>
            {'<p style="color:#888">'+pick.hindi_meaning+'</p>' if pick.hindi_meaning else ''}
            {'<p style="color:#6C63FF">Synonyms: '+pick.synonyms+'</p>' if pick.synonyms else ''}
            {'<p style="color:#888;font-style:italic">"'+pick.example_sentence+'"</p>' if pick.example_sentence else ''}
        </div>""", unsafe_allow_html=True)
