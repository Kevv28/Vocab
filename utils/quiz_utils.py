import random
from database.models import get_session, Word, QuizHistory
from datetime import datetime

def get_quiz_question(user_id, quiz_type='word_to_meaning'):
    session = get_session()
    try:
        words = session.query(Word).filter(Word.user_id == user_id).all()
        if len(words) < 4:
            return None
        target = random.choice(words)
        others = [w for w in words if w.id != target.id]
        wrong_choices = random.sample(others, min(3, len(others)))

        if quiz_type == 'word_to_meaning':
            question = f"What is the meaning of: **{target.word}**?"
            correct = target.meaning
            choices = [w.meaning for w in wrong_choices] + [correct]
        elif quiz_type == 'meaning_to_word':
            question = f"Which word means: *{target.meaning}*?"
            correct = target.word
            choices = [w.word for w in wrong_choices] + [correct]
        elif quiz_type == 'synonym':
            if not target.synonyms:
                return get_quiz_question(user_id, quiz_type)
            question = f"Which is a synonym of: **{target.word}**?"
            syns = [s.strip() for s in target.synonyms.split(',') if s.strip()]
            correct = syns[0] if syns else target.word
            choices = [w.word for w in wrong_choices] + [correct]
        elif quiz_type == 'antonym':
            if not target.antonyms:
                return get_quiz_question(user_id, quiz_type)
            question = f"Which is an antonym of: **{target.word}**?"
            ants = [a.strip() for a in target.antonyms.split(',') if a.strip()]
            correct = ants[0] if ants else target.word
            choices = [w.word for w in wrong_choices] + [correct]
        elif quiz_type == 'fill_blank':
            example = target.example_sentence or f"The word _____ means {target.meaning}."
            filled = example.replace(target.word, '_____')
            question = f"Fill in the blank: *{filled}*"
            correct = target.word
            choices = [w.word for w in wrong_choices] + [correct]
        else:
            return None

        random.shuffle(choices)
        return {
            'word_id': target.id,
            'question': question,
            'correct': correct,
            'choices': choices,
            'word': target.word,
            'quiz_type': quiz_type
        }
    finally:
        session.close()

def record_quiz_result(user_id, word_id, quiz_type, is_correct):
    session = get_session()
    try:
        qh = QuizHistory(user_id=user_id, word_id=word_id, quiz_type=quiz_type, is_correct=is_correct)
        session.add(qh)
        word = session.query(Word).filter(Word.id == word_id).first()
        if word:
            if is_correct:
                word.correct_count += 1
            else:
                word.wrong_count += 1
        session.commit()
    finally:
        session.close()

def get_quiz_stats(user_id):
    session = get_session()
    try:
        history = session.query(QuizHistory).filter(QuizHistory.user_id == user_id).all()
        total = len(history)
        correct = sum(1 for h in history if h.is_correct)
        return {
            'total': total,
            'correct': correct,
            'wrong': total - correct,
            'accuracy': round(correct/total*100, 1) if total > 0 else 0
        }
    finally:
        session.close()
