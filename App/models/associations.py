#Monique Britto

from sqlalchemy import Table, Column, Integer, ForeignKey
from App.database import db
# from .question import Question
# from .tag import Tag
from flask_login import UserMixin


Question_Tag_Bridge = Table(
    'question_tag_bridge',
    db.metadata,  # Important for SQLAlchemy to register it
    Column('id', Integer, primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('question_id', Integer, ForeignKey('question.id'))
)