import streamlit as st
import pandas as pd
import io, os, shutil
from utils.word_utils import get_words, import_words_from_df

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vocab.db')
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

COLUMNS = ['word','meaning','part_of_speech','synonyms','antonyms',
           'example_sentence','hindi_meaning','difficulty','source','personal_notes']

def show_import_export(user_id):
    st.markdown("<h1>⬆️ Import / Export</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⬇️ Export", "⬆️ Import", "💾 Backup / Restore"])

    with tab1:
        st.markdown("### Export Your Vocabulary")
        words = get_words(user_id)
        if not words:
            st.info("No words to export yet.")
        else:
            rows = [{
                'word': w.word, 'meaning': w.meaning, 'part_of_speech': w.part_of_speech,
                'synonyms': w.synonyms, 'antonyms': w.antonyms,
                'example_sentence': w.example_sentence, 'hindi_meaning': w.hindi_meaning,
                'difficulty': w.difficulty, 'source': w.source,
                'personal_notes': w.personal_notes, 'revision_count': w.revision_count,
                'revision_level': w.revision_level, 'is_favorite': w.is_favorite,
                'date_added': str(w.date_added)
            } for w in words]
            df = pd.DataFrame(rows)

            # CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "vocab_export.csv", "text/csv", width='stretch')

            # Excel
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Vocabulary')
            st.download_button("⬇️ Download Excel", buf.getvalue(),
                               "vocab_export.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')
            st.success(f"Ready to export {len(words)} words.")

    with tab2:
        st.markdown("### Import Words")
        st.markdown("""
        <div style='background:#2a2a3e;border:1px solid #3a3a5e;border-radius:10px;padding:16px;margin-bottom:16px'>
            <b style='color:#6C63FF'>Required columns:</b>
            <p style='color:#888;margin:4px 0'>word, meaning</p>
            <b style='color:#6C63FF'>Optional columns:</b>
            <p style='color:#888;margin:4px 0'>part_of_speech, synonyms, antonyms, example_sentence, hindi_meaning, difficulty (Easy/Medium/Hard), source (CAT/GRE/Newspaper/Book/RC/Other), personal_notes</p>
        </div>""", unsafe_allow_html=True)

        # Download template
        template_df = pd.DataFrame([{
            'word': 'ephemeral', 'meaning': 'Lasting for a very short time',
            'part_of_speech': 'adjective', 'synonyms': 'transient, fleeting',
            'antonyms': 'permanent, lasting', 'example_sentence': 'The ephemeral beauty of youth.',
            'hindi_meaning': 'क्षणिक', 'difficulty': 'Medium', 'source': 'CAT', 'personal_notes': ''
        }])
        tpl_csv = template_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download Template CSV", tpl_csv, "vocab_template.csv", "text/csv")

        uploaded = st.file_uploader("Upload CSV or Excel file", type=['csv','xlsx','xls'])
        if uploaded:
            try:
                if uploaded.name.endswith('.csv'):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)
                st.markdown(f"**Preview** ({len(df)} rows):")
                st.dataframe(df.head(5), use_container_width=True)
                if st.button("✅ Import Words", width='stretch'):
                    success, failed = import_words_from_df(user_id, df)
                    st.success(f"Imported {success} words successfully!")
                    if failed:
                        st.warning(f"{failed} rows failed.")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with tab3:
        st.markdown("### Database Backup & Restore")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💾 Backup Database")
            if os.path.exists(DB_PATH):
                with open(DB_PATH, 'rb') as f:
                    db_bytes = f.read()
                st.download_button("⬇️ Download vocab.db", db_bytes,
                                   "vocab_backup.db", "application/octet-stream",
                                   width='stretch')
                st.info(f"Database size: {round(os.path.getsize(DB_PATH)/1024, 1)} KB")
            else:
                st.warning("No database file found.")

        with col2:
            st.markdown("#### 🔄 Restore Database")
            st.warning("⚠️ Restoring will REPLACE all current data!")
            restore_file = st.file_uploader("Upload .db backup", type=['db'])
            if restore_file:
                if st.button("🔄 Restore Now", width='stretch'):
                    with open(DB_PATH, 'wb') as f:
                        f.write(restore_file.read())
                    st.success("Database restored! Please restart the app.")
