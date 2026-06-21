from database.models import get_session, Word, Statistics
from datetime import datetime, timedelta, date
import pandas as pd

REVISION_INTERVALS = {0: 1, 1: 3, 2: 7, 3: 15, 4: 30}

def add_word(user_id, data: dict) -> tuple[bool, str]:
    session = get_session()
    try:
        word = Word(user_id=user_id, **data)
        word.next_revision = datetime.utcnow() + timedelta(days=1)
        session.add(word)
        session.commit()
        _update_stats(session, user_id, words_added=1)
        return True, "Word added!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def get_words(user_id, search=None, difficulty=None, source=None, favorites_only=False, sort_by='date_added'):
    session = get_session()
    try:
        q = session.query(Word).filter(Word.user_id == user_id)
        if search:
            q = q.filter(Word.word.ilike(f'%{search}%') | Word.meaning.ilike(f'%{search}%') | Word.synonyms.ilike(f'%{search}%'))
        if difficulty and difficulty != 'All':
            q = q.filter(Word.difficulty == difficulty)
        if source and source != 'All':
            q = q.filter(Word.source == source)
        if favorites_only:
            q = q.filter(Word.is_favorite == True)
        if sort_by == 'date_added':
            q = q.order_by(Word.date_added.desc())
        elif sort_by == 'word':
            q = q.order_by(Word.word.asc())
        elif sort_by == 'difficulty':
            q = q.order_by(Word.difficulty)
        return q.all()
    finally:
        session.close()

def get_word_by_id(word_id):
    session = get_session()
    try:
        return session.query(Word).filter(Word.id == word_id).first()
    finally:
        session.close()

def update_word(word_id, data: dict) -> tuple[bool, str]:
    session = get_session()
    try:
        word = session.query(Word).filter(Word.id == word_id).first()
        if not word:
            return False, "Word not found."
        for k, v in data.items():
            setattr(word, k, v)
        session.commit()
        return True, "Updated!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def delete_word(word_id) -> tuple[bool, str]:
    session = get_session()
    try:
        word = session.query(Word).filter(Word.id == word_id).first()
        if word:
            session.delete(word)
            session.commit()
        return True, "Deleted!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def toggle_favorite(word_id):
    session = get_session()
    try:
        word = session.query(Word).filter(Word.id == word_id).first()
        if word:
            word.is_favorite = not word.is_favorite
            session.commit()
    finally:
        session.close()

def get_due_revisions(user_id):
    session = get_session()
    try:
        now = datetime.utcnow()
        return session.query(Word).filter(
            Word.user_id == user_id,
            Word.next_revision <= now
        ).all()
    finally:
        session.close()

def mark_revised(word_id, user_id):
    session = get_session()
    try:
        word = session.query(Word).filter(Word.id == word_id).first()
        if word:
            word.last_revised = datetime.utcnow()
            word.revision_count += 1
            level = min(word.revision_level + 1, 4)
            word.revision_level = level
            word.next_revision = datetime.utcnow() + timedelta(days=REVISION_INTERVALS[level])
            session.commit()
            _update_stats(session, user_id, words_revised=1)
    finally:
        session.close()

def get_words_added_today(user_id):
    session = get_session()
    try:
        today = date.today()
        return session.query(Word).filter(
            Word.user_id == user_id,
            Word.date_added >= datetime(today.year, today.month, today.day)
        ).count()
    finally:
        session.close()

def _update_stats(session, user_id, words_added=0, words_revised=0, quiz_attempted=0, quiz_correct=0):
    today = date.today()
    stat = session.query(Statistics).filter(
        Statistics.user_id == user_id,
        Statistics.date == today
    ).first()
    if not stat:
        stat = Statistics(user_id=user_id, date=today,
                          words_added=0, words_revised=0, quiz_attempted=0, quiz_correct=0)
        session.add(stat)
    stat.words_added = (stat.words_added or 0) + words_added
    stat.words_revised = (stat.words_revised or 0) + words_revised
    stat.quiz_attempted = (stat.quiz_attempted or 0) + quiz_attempted
    stat.quiz_correct = (stat.quiz_correct or 0) + quiz_correct
    session.commit()

def get_daily_stats(user_id, days=30):
    session = get_session()
    try:
        from_date = date.today() - timedelta(days=days)
        stats = session.query(Statistics).filter(
            Statistics.user_id == user_id,
            Statistics.date >= from_date
        ).order_by(Statistics.date).all()
        return stats
    finally:
        session.close()

def get_streak(user_id):
    session = get_session()
    try:
        today = date.today()
        streak = 0
        check_date = today
        while True:
            stat = session.query(Statistics).filter(
                Statistics.user_id == user_id,
                Statistics.date == check_date
            ).first()
            if stat and (stat.words_added > 0 or stat.words_revised > 0):
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        return streak
    finally:
        session.close()

def get_accuracy(user_id):
    session = get_session()
    try:
        words = session.query(Word).filter(Word.user_id == user_id).all()
        total_correct = sum(w.correct_count for w in words)
        total_wrong = sum(w.wrong_count for w in words)
        total = total_correct + total_wrong
        return round((total_correct / total * 100) if total > 0 else 0, 1)
    finally:
        session.close()

def get_learning_score(user_id):
    accuracy = get_accuracy(user_id)
    streak = get_streak(user_id)
    due = get_due_revisions(user_id)
    session = get_session()
    try:
        total_words = session.query(Word).filter(Word.user_id == user_id).count()
        stats = get_daily_stats(user_id, 30)
        active_days = len([s for s in stats if s.words_added > 0 or s.words_revised > 0])
        consistency = (active_days / 30) * 100
        revision_completion = max(0, 100 - len(due) * 5)
        streak_score = min(streak * 5, 100)
        score = (accuracy * 0.4) + (streak_score * 0.2) + (revision_completion * 0.2) + (consistency * 0.2)
        return round(min(score, 100), 1)
    finally:
        session.close()

def import_words_from_df(user_id, df: pd.DataFrame) -> tuple[int, int]:
    session = get_session()
    success = 0
    failed = 0
    try:
        for _, row in df.iterrows():
            try:
                word = Word(
                    user_id=user_id,
                    word=str(row.get('word', '')),
                    meaning=str(row.get('meaning', '')),
                    part_of_speech=str(row.get('part_of_speech', '')),
                    synonyms=str(row.get('synonyms', '')),
                    antonyms=str(row.get('antonyms', '')),
                    example_sentence=str(row.get('example_sentence', '')),
                    hindi_meaning=str(row.get('hindi_meaning', '')),
                    difficulty=str(row.get('difficulty', 'Medium')),
                    source=str(row.get('source', 'Other')),
                    next_revision=datetime.utcnow() + timedelta(days=1)
                )
                session.add(word)
                success += 1
            except:
                failed += 1
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()
    return success, failed
