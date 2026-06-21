import streamlit as st
from utils.word_utils import add_word
from utils.ui_helpers import save_uploaded_file

def show_add_word(user_id):
    st.markdown("<h1>➕ Add New Word</h1>", unsafe_allow_html=True)

    with st.form("add_word_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            word = st.text_input("Word *", placeholder="e.g. Ephemeral")
            meaning = st.text_area("Meaning *", placeholder="Short description of what the word means")
            hindi_meaning = st.text_input("Hindi Meaning 🇮🇳", placeholder="हिन्दी अर्थ")
            synonyms = st.text_input("Synonyms", placeholder="Comma-separated: transient, fleeting, momentary")
            antonyms = st.text_input("Antonyms", placeholder="Comma-separated: permanent, lasting, eternal")
            example_sentence = st.text_area("Example Sentence", placeholder="Use the word in a sentence...")

        with c2:
            part_of_speech = st.selectbox("Part of Speech", ["", "noun", "verb", "adjective", "adverb",
                                                               "preposition", "conjunction", "interjection", "phrase"])
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            source = st.selectbox("Source", ["CAT", "GRE", "Newspaper", "Book", "RC", "Other"])
            personal_notes = st.text_area("Personal Notes", placeholder="Your own notes, memory tricks, etc.")
            image_file = st.file_uploader("Attach Image 📷", type=['png', 'jpg', 'jpeg'])

        submitted = st.form_submit_button("➕ Add Word", width='stretch')

    if submitted:
        if not word or not meaning:
            st.error("Word and Meaning are required!")
        else:
            img_path = None
            if image_file:
                img_path = save_uploaded_file(image_file)
            data = {
                'word': word.strip(),
                'meaning': meaning.strip(),
                'hindi_meaning': hindi_meaning.strip(),
                'synonyms': synonyms.strip(),
                'antonyms': antonyms.strip(),
                'example_sentence': example_sentence.strip(),
                'part_of_speech': part_of_speech,
                'difficulty': difficulty,
                'source': source,
                'personal_notes': personal_notes.strip(),
                'image_path': img_path
            }
            ok, msg = add_word(user_id, data)
            if ok:
                st.success(f"✅ '{word}' added successfully!")
                st.balloons()
            else:
                st.error(msg)

    # Quick tips
    st.markdown("---")
    st.markdown("#### 💡 Tips for Effective Vocabulary Learning")
    cols = st.columns(3)
    tips = [
        ("🔗 Add Synonyms", "Synonyms help you remember words by creating a mental web of related words."),
        ("💬 Use Examples", "Always write your own example sentence — it aids retention significantly."),
        ("📝 Personal Notes", "Add memory tricks or mnemonics in the notes field for difficult words."),
    ]
    for col, (title, desc) in zip(cols, tips):
        with col:
            st.markdown(f"""
            <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:10px;padding:16px'>
                <b style='color:#6C63FF'>{title}</b>
                <p style='color:#888;font-size:0.85rem;margin-top:8px'>{desc}</p>
            </div>""", unsafe_allow_html=True)
