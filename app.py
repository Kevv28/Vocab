import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database.models import init_db
from utils.auth import check_login, login_user, register_user, logout
from utils.ui_helpers import apply_custom_css, get_quote, get_word_of_day

st.set_page_config(
    page_title="VocabMaster Pro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
apply_custom_css()

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:40px 0 20px'>
            <div style='font-size:3rem'>📚</div>
            <h1 style='color:#6C63FF;font-size:2.5rem;margin:0'>VocabMaster Pro</h1>
            <p style='color:#888'>Your personal vocabulary learning system</p>
        </div>""", unsafe_allow_html=True)

        tab1, tab2 = st.tabs([" Login", "Register"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Login", width='stretch')
                if submitted:
                    ok, msg, uid = login_user(username, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_id = uid
                        st.session_state.username = username
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Username", placeholder="Choose username")
                new_email = st.text_input("Email (optional)", placeholder="email@example.com")
                new_pass = st.text_input("Password", type="password", placeholder="Choose password")
                new_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                submitted = st.form_submit_button("Register", width='stretch')
                if submitted:
                    if new_pass != new_pass2:
                        st.error("Passwords don't match!")
                    elif len(new_pass) < 4:
                        st.error("Password too short (min 4 chars)")
                    else:
                        ok, msg = register_user(new_user, new_pass, new_email)
                        if ok:
                            st.success(msg + " Please login.")
                        else:
                            st.error(msg)

        # Word of the Day on login
        wod = get_word_of_day()
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#6C63FF22,#8B5CF622);border:1px solid #6C63FF44;
        border-radius:12px;padding:20px;margin-top:24px;text-align:center'>
            <p style='color:#888;margin:0;font-size:0.85rem'>✨ WORD OF THE DAY</p>
            <h2 style='color:#6C63FF;margin:8px 0'>{wod['word']}</h2>
            <p style='color:#ccc;margin:4px 0'>{wod['meaning']}</p>
            <p style='color:#888;font-style:italic;margin:4px 0;font-size:0.9rem'>"{wod['example']}"</p>
        </div>""", unsafe_allow_html=True)

def main_app():
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")

    # Sidebar
    with st.sidebar:
        st.markdown(f'<div class="sidebar-title">📚 VocabMaster</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='color:#888;font-size:0.85rem'>👤 {username}</p>", unsafe_allow_html=True)
        st.divider()

        page = st.radio("Navigation", [
            "🏠 Dashboard",
            "📖 Vocabulary",
            "➕ Add Word",
            "🔄 Revisions",
            "📝 Daily Notes",
            "🧠 Quiz",
            "📄 PDF Annotator",
            "📊 Analytics",
            "⬆️ Import / Export",
            "⭐ Favorites",
        ], label_visibility="collapsed")

        st.divider()
        quote = get_quote()
        st.markdown(f"<p style='color:#666;font-size:0.75rem;font-style:italic'>{quote}</p>", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 Logout", width='stretch'):
            logout()
            st.rerun()

    # Page routing
    p = page.split(" ", 1)[1].strip()
    if p == "Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard(user_id)
    elif p == "Vocabulary":
        from pages.vocabulary import show_vocabulary
        show_vocabulary(user_id)
    elif p == "Add Word":
        from pages.add_word import show_add_word
        show_add_word(user_id)
    elif p == "Revisions":
        from pages.revisions import show_revisions
        show_revisions(user_id)
    elif p == "Daily Notes":
        from pages.notes import show_notes
        show_notes(user_id)
    elif p == "Quiz":
        from pages.quiz import show_quiz
        show_quiz(user_id)
    elif p == "PDF Annotator":
        from pages.pdf_annotator import show_pdf_annotator
        show_pdf_annotator(user_id)
    elif p == "Analytics":
        from pages.analytics import show_analytics
        show_analytics(user_id)
    elif p == "Import / Export":
        from pages.import_export import show_import_export
        show_import_export(user_id)
    elif p == "Favorites":
        from pages.favorites import show_favorites
        show_favorites(user_id)

if check_login():
    main_app()
else:
    login_page()
