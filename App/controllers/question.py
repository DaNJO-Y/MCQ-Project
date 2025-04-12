from App.models import Question
from App.models import exam_question
from App.database import db
from App.utils import shuffle
from datetime import date
from sqlalchemy import select


def save_question(teacherId, text, difficulty, courseCode, options):
    newquestion = Question(teacherId=teacherId, text=text, difficulty=difficulty,courseCode=courseCode, options=options)
    newquestion.dateCreated = date.today()
    db.session.add(newquestion)
    db.session.commit()
    return newquestion

def edit_question(id, text, difficulty, courseCode):
    question = get_question(id)
    if question:
        if text != None:
            question.text = text
        if difficulty != None:
            question.difficulty = difficulty
        if courseCode != None:
            question.courseCode = courseCode
        db.session.add(question)
        try:
            db.session.commit()
            return question  # Return the updated question object
        except Exception as e:
            db.session.rollback() #rollback the session if there is an error.
            print(f"Error editing question: {e}")
            return None  # Indicate failure
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

def get_all_my_questions(user):
    return Question.query.filter_by(teacherId=user.id).all()  # Fetch all questions for the teacher

def get_all_my_questions_json(user):
    questions = Question.query.filter_by(teacherId=user.id).all()  
    return [question.get_json() for question in questions]

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
        
def get_questions_exams(questionId):
    exam_ids = []
    # questions = exam_question.query.filter_by(question_id=questionId).all()
    # for question in questions:
    #     exam_ids.append(question.exam_id)
    # return exam_ids
    stmt = select(exam_question.c.exam_id).where(exam_question.c.question_id == questionId)
    #Execute the statement using the db's engine
    results = db.session.execute(stmt).fetchall()

    for row in results:
        exam_ids.append(row[0]) #row is a tuple.
    return exam_ids


    



