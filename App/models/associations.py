#Monique Britto

from sqlalchemy import Table, Column, Integer, ForeignKey
from App.database import db
from flask_login import UserMixin


Question_Tag_Bridge = Table(
    'question_tag_bridge',
    db.metadata, 
    Column('id', Integer, primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id')),
    Column('question_id', Integer, ForeignKey('question.id'))
)


def __init__(self, tag_id, question_id):
        self.tag_id = tag_id
        self.question_id = question_id