import bcrypt
import streamlit as st
from database.models import get_session, User, init_db

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    init_db()
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            return False, "Username already exists."
        user = User(username=username, email=email, password_hash=hash_password(password))
        session.add(user)
        session.commit()
        return True, "Registration successful!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def login_user(username: str, password: str) -> tuple[bool, str, object]:
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False, "User not found.", None
        if verify_password(password, user.password_hash):
            return True, "Login successful!", user.id
        return False, "Incorrect password.", None
    finally:
        session.close()

def check_login():
    return st.session_state.get("logged_in", False)

def get_current_user_id():
    return st.session_state.get("user_id")

def logout():
    for key in ["logged_in", "user_id", "username"]:
        st.session_state.pop(key, None)
