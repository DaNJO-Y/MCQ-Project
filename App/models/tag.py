#Monique Britto

from sqlalchemy import Table, Column, Integer, ForeignKey
from App.database import db
from flask_login import UserMixin
from .associations import Question_Tag_Bridge

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag_text = db.Column(db.String(120), nullable=False)
    question = db.relationship('Question', secondary='question_tag_bridge', back_populates='tag')
