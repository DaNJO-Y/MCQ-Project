#Monique Britto
from App.database import db
from flask_login import UserMixin

Question_Tag_Bridge= Table('question_tag_bridge',
        Column('id',Integer,primary_key=True),
        Column('tag_id',Integer, ForeignKey(tag.id)),
        Column(question_id),Integer,ForeignKey(question.id))


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag_text = db.Column(db.String(120), nullable = False)
    question = db.relationship('Question', secondary='Question_Tag_Bridge', backref=db.backref('tag', lazy=True))

