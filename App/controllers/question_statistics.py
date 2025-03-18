from App.models import QuestionStatistics
from App.database import db

def addStats(question_id, year, data):
    new_qStat = QuestionStatistics(question_id=question_id,data=data, year=year)
    db.session.add(new_qStat)
    db.session.commit()
    return new_qStat

def get_question_stat(id):
    return QuestionStatistics.query.get(id)


def editStats(id, question_id, year, data):
    qStat = get_question_stat(id)
    if qStat and qStat.question_id==question_id:
        qStat.year = year
        qStat.data.append(data)
        db.session.add(qStat)
        return db.session.commit()
    return None

def deleteStat(id, question_id):
    qStat = get_question_stat(id)
    if not qStat:
        print(f'Question Statistic with {id} not found')
        return
    db.session.delete(qStat)
    db.session.commit()
    print(f'Question Statistic with {id} deleted')    