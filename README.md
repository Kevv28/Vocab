# 📚 VocabMaster Pro

A complete vocabulary learning system for CAT/GRE/English preparation.

## 🚀 Quick Start

### Windows
Double-click `run.bat`

### Linux / Mac
```bash
chmod +x run.sh
./run.sh
```

### Manual
```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## ✨ Features
- 🔐 User registration & login
- 📖 Full vocabulary database (word, meaning, Hindi, synonyms, antonyms, examples)
- 🔄 Spaced repetition (5 levels: 1, 3, 7, 15, 30 days)
- 🧠 Quiz system (5 types)
- 📝 Daily study notes with image attachments
- 📄 PDF Annotator (draw, tick, cross on PDFs)
- 📊 Analytics dashboard with charts & heatmap
- ⭐ Favorites collection
- ⬆️ Import CSV/Excel, Export CSV/Excel
- 💾 Database backup & restore
- 🌙 Dark mode UI

## 📁 Folder Structure
```
vocab_app/
├── app.py              # Main entry point
├── database/models.py  # SQLAlchemy models (SQLite)
├── pages/              # All pages
├── utils/              # Auth, word, note, quiz utilities
├── charts/             # Plotly chart functions
├── uploads/            # Uploaded images & annotated PDFs
├── requirements.txt
├── run.bat             # Windows launcher
└── run.sh              # Linux/Mac launcher
```

## 📦 Dependencies
- Streamlit, SQLAlchemy, bcrypt, Plotly, Pandas
- PyMuPDF (PDF reading), streamlit-drawable-canvas (PDF annotation)
- Pillow, openpyxl
