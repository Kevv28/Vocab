from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    words = relationship('Word', back_populates='user')
    notes = relationship('DailyNote', back_populates='user')
    quiz_history = relationship('QuizHistory', back_populates='user')
    statistics = relationship('Statistics', back_populates='user')

class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    word = Column(String(100), nullable=False)
    meaning = Column(Text)
    part_of_speech = Column(String(50))
    synonyms = Column(Text)
    antonyms = Column(Text)
    example_sentence = Column(Text)
    hindi_meaning = Column(Text)
    personal_notes = Column(Text)
    difficulty = Column(String(20), default='Medium')
    source = Column(String(50), default='Other')
    date_added = Column(DateTime, default=datetime.utcnow)
    last_revised = Column(DateTime)
    revision_count = Column(Integer, default=0)
    revision_level = Column(Integer, default=0)
    next_revision = Column(DateTime)
    is_favorite = Column(Boolean, default=False)
    image_path = Column(String(255))
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    user = relationship('User', back_populates='words')

class DailyNote(Base):
    __tablename__ = 'daily_notes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date, default=datetime.utcnow().date)
    words_learned = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    topic = Column(String(200))
    content = Column(Text)
    mood_rating = Column(Integer, default=3)
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='notes')

class QuizHistory(Base):
    __tablename__ = 'quiz_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    word_id = Column(Integer, ForeignKey('words.id'))
    quiz_type = Column(String(50))
    is_correct = Column(Boolean)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='quiz_history')

class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date, default=datetime.utcnow().date)
    words_added = Column(Integer, default=0)
    words_revised = Column(Integer, default=0)
    quiz_attempted = Column(Integer, default=0)
    quiz_correct = Column(Integer, default=0)
    study_minutes = Column(Integer, default=0)
    user = relationship('User', back_populates='statistics')

def get_engine():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vocab.db')
    return create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})

def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
