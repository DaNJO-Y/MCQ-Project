from App.database import db
from App.models.exam_statistics import ExamStatistics
from App.models.exam import Exam

def add_stats(exam_id, data, year):
    try:
        # Check if exam exists
        exam = Exam.query.get(exam_id)
        if not exam:
            return {"error": "Exam not found"}, 404
        
        # Create new statistics
        stats = ExamStatistics(
            exam_id=exam_id,
            data=data,
            year=year
        )
        
        db.session.add(stats)
        db.session.commit()
        
        return {"message": "Statistics added successfully", "stats": stats.get_json()}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400


def edit_stats(stats_id, data, year=None):
    try:
        stats = ExamStatistics.query.get(stats_id)
        if not stats:
            return {"error": "Statistics not found"}, 404

        # Update data
        if data:
            stats.data = data
        
        # Update year if provided
        if year is not None:
            stats.year = year

        db.session.commit()
        
        return {
            "message": "Statistics updated successfully",
            "stats": stats.get_json()
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400


def delete_stat(stats_id):
    try:
        stats = ExamStatistics.query.get(stats_id)
        if not stats:
            return {"error": "Statistics not found"}, 404

        db.session.delete(stats)
        db.session.commit()
        
        return {"message": "Statistics deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400
