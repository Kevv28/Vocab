import streamlit as st
import os
from PIL import Image
import uuid
from datetime import datetime

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

QUOTES = [
    "The limits of my language mean the limits of my world. — Wittgenstein",
    "One word frees us of all the weight and pain of life: that word is love. — Sophocles",
    "Words are, of course, the most powerful drug used by mankind. — Kipling",
    "A word after a word after a word is power. — Margaret Atwood",
    "Words are the clothes thoughts wear. — Samuel Beckett",
    "Language is the road map of a culture. — Rita Mae Brown",
    "The pen is mightier than the sword. — Bulwer-Lytton",
    "Words are free. It's how you use them that may cost you.",
    "In the beginning was the Word. — John 1:1",
    "All I need is a sheet of paper and something to write with. — Bukowski",
]

WORD_OF_DAY = [
    {"word": "Ephemeral", "meaning": "Lasting for a very short time", "example": "The ephemeral beauty of cherry blossoms."},
    {"word": "Sycophant", "meaning": "A person who flatters to gain favor", "example": "The king was surrounded by sycophants."},
    {"word": "Eloquent", "meaning": "Fluent and persuasive in speaking", "example": "She gave an eloquent speech."},
    {"word": "Pedantic", "meaning": "Overly concerned with minor details or rules", "example": "His pedantic approach annoyed everyone."},
    {"word": "Laconic", "meaning": "Using very few words", "example": "His laconic reply was just 'No.'"},
    {"word": "Perspicacious", "meaning": "Having a ready insight; shrewd", "example": "A perspicacious observer noticed the flaw."},
    {"word": "Loquacious", "meaning": "Tending to talk a great deal; talkative", "example": "She was loquacious at the party."},
    {"word": "Obfuscate", "meaning": "To make unclear or confusing", "example": "He tried to obfuscate the issue."},
    {"word": "Recalcitrant", "meaning": "Having an obstinately uncooperative attitude", "example": "The recalcitrant student refused to comply."},
    {"word": "Sagacious", "meaning": "Having good judgment; wise", "example": "A sagacious leader makes wise decisions."},
]

def get_quote():
    from datetime import date
    idx = date.today().toordinal() % len(QUOTES)
    return QUOTES[idx]

def get_word_of_day():
    from datetime import date
    idx = date.today().toordinal() % len(WORD_OF_DAY)
    return WORD_OF_DAY[idx]

def save_uploaded_file(uploaded_file) -> str:
    ext = uploaded_file.name.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def show_image_preview(image_path):
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, width=300)

def metric_card(label, value, delta=None, color="#6C63FF"):
    delta_html = f"<p style='color:#43D9A2;font-size:0.8rem;margin:0'>{delta}</p>" if delta else ""
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{color}22,{color}11);border:1px solid {color}44;
    border-radius:12px;padding:16px;margin:4px 0;'>
        <p style='color:#aaa;font-size:0.8rem;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <p style='color:#fff;font-size:2rem;font-weight:700;margin:4px 0'>{value}</p>
        {delta_html}
    </div>""", unsafe_allow_html=True)

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #13131f; }
    
    .stSidebar { background-color: #1a1a2e !important; border-right: 1px solid #2a2a4e; }
    .stSidebar .stMarkdown { color: #e0e0ff; }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, 
    .stSelectbox > div > div { 
        background-color: #2a2a3e !important; 
        color: #e0e0ff !important;
        border: 1px solid #3a3a5e !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #8B5CF6);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 1.5rem; font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px #6C63FF55; }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #2a2a3e, #1e1e2e);
        border: 1px solid #3a3a5e; border-radius: 12px; padding: 16px;
    }
    
    .word-card {
        background: linear-gradient(135deg, #2a2a3e, #1e1e2e);
        border: 1px solid #3a3a5e; border-radius: 12px;
        padding: 16px; margin: 8px 0;
        transition: all 0.2s ease;
    }
    .word-card:hover { border-color: #6C63FF; transform: translateY(-1px); }
    
    h1, h2, h3 { color: #e0e0ff !important; }
    p, label { color: #c0c0d0 !important; }
    
    .stProgress .st-bo { background-color: #6C63FF; }
    .stTabs [data-baseweb="tab"] { color: #a0a0c0; }
    .stTabs [aria-selected="true"] { color: #6C63FF; border-bottom-color: #6C63FF; }
    
    .badge {
        display:inline-block; padding:2px 8px; border-radius:20px;
        font-size:0.75rem; font-weight:600; margin:2px;
    }
    .badge-easy { background:#43D9A222; color:#43D9A2; border:1px solid #43D9A255; }
    .badge-medium { background:#FFB34722; color:#FFB347; border:1px solid #FFB34755; }
    .badge-hard { background:#FF658422; color:#FF6584; border:1px solid #FF658455; }
    .badge-source { background:#6C63FF22; color:#6C63FF; border:1px solid #6C63FF55; }
    
    div[data-testid="stExpander"] {
        background: #2a2a3e; border: 1px solid #3a3a5e; border-radius: 8px;
    }
    
    .sidebar-title {
        font-size:1.4rem; font-weight:700; color:#6C63FF;
        padding: 8px 0; margin-bottom:8px;
    }
    </style>
    """, unsafe_allow_html=True)

def difficulty_badge(diff):
    cls = {'Easy': 'badge-easy', 'Medium': 'badge-medium', 'Hard': 'badge-hard'}.get(diff, 'badge-source')
    return f'<span class="badge {cls}">{diff}</span>'
