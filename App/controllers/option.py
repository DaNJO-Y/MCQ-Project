from App.models import Option
from App.database import db

def create_option(question_id, body, image, is_correct):
    new_option = Option(questionId=question_id, body=body, image=image, is_correct=is_correct)
    db.session.add(new_option)
    db.session.commit()
    return new_option

def get_option(id):
    return Option.query.get(id)

def add_text(id, text, question_id):
    option = get_option(id)
    if option and option.question_id == question_id:
        option.body = text
        db.session.add(option)
        db.session.commit()
        return option
    return None

def add_image(id, image, question_id):
    option = get_option(id)
    if option and option.question_id == question_id:
        option.image = image
        db.session.add(option)
        db.session.commit()
        return option
    return None

def remove_text(id, question_id):
    option = get_option(id)
    if option and option.questionId == question_id:
        option.body = None  # Set body to None to remove text
        db.session.add(option)
        db.session.commit()
        return option
    return None

def remove_image(id, question_id):
    option = get_option(id)
    if option and option.questionId == question_id:
        option.image = None  # Set image to None to remove image
        db.session.add(option)
        db.session.commit()
        return option
    return None