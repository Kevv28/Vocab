from database.models import get_session, DailyNote
from datetime import datetime, date

def add_note(user_id, note_date, words_learned, time_spent, topic, content, mood_rating, image_path=None):
    session = get_session()
    try:
        existing = session.query(DailyNote).filter(
            DailyNote.user_id == user_id,
            DailyNote.date == note_date
        ).first()
        if existing:
            existing.words_learned = words_learned
            existing.time_spent = time_spent
            existing.topic = topic
            existing.content = content
            existing.mood_rating = mood_rating
            if image_path:
                existing.image_path = image_path
        else:
            note = DailyNote(
                user_id=user_id, date=note_date, words_learned=words_learned,
                time_spent=time_spent, topic=topic, content=content,
                mood_rating=mood_rating, image_path=image_path
            )
            session.add(note)
        session.commit()
        return True, "Note saved!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def get_notes(user_id, search=None):
    session = get_session()
    try:
        q = session.query(DailyNote).filter(DailyNote.user_id == user_id)
        if search:
            q = q.filter(DailyNote.content.ilike(f'%{search}%') | DailyNote.topic.ilike(f'%{search}%'))
        return q.order_by(DailyNote.date.desc()).all()
    finally:
        session.close()

def get_note_by_date(user_id, note_date):
    session = get_session()
    try:
        return session.query(DailyNote).filter(
            DailyNote.user_id == user_id,
            DailyNote.date == note_date
        ).first()
    finally:
        session.close()

def delete_note(note_id):
    session = get_session()
    try:
        note = session.query(DailyNote).filter(DailyNote.id == note_id).first()
        if note:
            session.delete(note)
            session.commit()
        return True, "Deleted!"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def get_heatmap_data(user_id):
    session = get_session()
    try:
        notes = session.query(DailyNote).filter(DailyNote.user_id == user_id).all()
        return {str(n.date): n.words_learned for n in notes}
    finally:
        session.close()
