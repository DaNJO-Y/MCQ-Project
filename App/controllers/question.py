from App.models import Question
from App.database import db
from App.utils import shuffle

def save_question(teacherId, correctOption, difficulty, courseCode, options):
    newquestion = Question(teacherId=teacherId, correctOption=correctOption, difficulty=difficulty,courseCode=courseCode, options=options)
    db.session.add(newquestion)
    db.session.commit()
    return newquestion

def edit_question(id,correctOption, difficulty,courseCode):
    question = get_question(id)
    if question:
        question.correctOption = correctOption
        question.difficulty = difficulty
        question.courseCode = courseCode
        db.session.add(question)
        return db.session.commit()
    return None

def delete_question(id):
    question = get_question(id)
    if not question:
        print(f'User with {id} not found')
        return
    db.session.delete(question)
    db.session.commit()
    print(f'User with {id} deleted')


def shuffle_options(options):
    shuffled = shuffle(options)
    return shuffled
    

def update_last_used(id, new_last_used):
    question = get_question(id)
    if question:
        question.lastUsed = new_last_used
        db.session.add(question)
        return db.session.commit()
    return None




def get_question(id):
   return Question.query.get(id) 


def add_image(id,image):
    question = get_question(id)
    if question:
        question.image = image
        db.session.add(question)
        return db.session.commit()
    return None

def add_tag(id,tag):
    question = get_question(id)
    if question:
        question.tag.append(tag)
        db.session.add(question)
        return db.session.commit()
    return None

def toggle_isCorrectOption(id, option_id):
    question = get_question(id)
    if question:
        for option in question.options:
            if option.id == option_id:
                option.toggle()
                db.session.commit()
                return {"message": "Option is_correct toggled"} 
        return {"error": "Option not found for this question"} 
    return {"error": "Question not found"}
        
    

    



