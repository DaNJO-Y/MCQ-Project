from App.database import db
from sqlalchemy import Table, Column, Integer, ForeignKey
from App.database import db
from flask_login import UserMixin



exam_question = Table(
    'exam_question',
    db.metadata,
    Column('exam_id', Integer, ForeignKey('exam.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('question.id'), primary_key=True)
)
