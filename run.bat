@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting VocabMaster Pro...
streamlit run app.py
pause
