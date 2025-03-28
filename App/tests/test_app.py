import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *
from datetime import datetime

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
# class UserUnitTests(unittest.TestCase):

#     def test_new_user(self):
#         user = User("bob", "bobpass")
#         assert user.username == "bob"

#     # pure function no side effects or integrations called
#     def test_get_json(self):
#         user = User("bob", "bobpass")
#         user_json = user.get_json()
#         self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
#     def test_hashed_password(self):
#         password = "mypass"
#         hashed = generate_password_hash(password, method='sha256')
#         user = User("bob", password)
#         assert user.password != password

#     def test_check_password(self):
#         password = "mypass"
#         user = User("bob", password)
#         assert user.check_password(password)

class TeacherUnitTests(unittest.TestCase):
    def test_new_teacher(self):
        teacher = Teacher("Terry", "Wu", "Terry234", "terpass", "terry@email.com")
        assert teacher.firstName == "Terry"
        assert teacher.lastName == "Wu"
        assert teacher.check_password("terpass")
        assert teacher.email == "terry@email.com"

    def test_get_json(self):
        teacher = Teacher("Terry", "Wu", "Terry234", "terpass", "terry@email.com")
        teacher_json = teacher.get_json()
        self.assertDictEqual(teacher_json, {"id":None, "firstName":"Terry", "lastName":"Wu", "userName":"Terry234", "email":"terry@email.com"})

    def test_hashed_password(self):
        password = "terpass"
        hashed = generate_password_hash(password, method='sha256')
        teacher = Teacher("Terry", "Wu", "Terry234", password, "terry@email.com")
        assert teacher.password != password

    def test_check_password(self):
        password = "terpass"
        teacher = Teacher("Terry", "Wu", "Terry234", password, "terry@email.com")
        assert teacher.check_password(password)


class ExamUnitTests(unittest.TestCase):
    def test_new_exam(self):
        exam = Exam(teacher_id=1, title="Final Exam", course_code="CS101")
        exam.date_created = datetime.utcnow()
        assert exam.teacher_id == 1
        assert exam.title == "Final Exam"
        assert exam.course_code == "CS101"
        assert exam.saved is False
        assert exam.date_created is not None

    def test_get_json(self):
        exam = Exam(teacher_id=1, title="Final Exam", course_code="CS101")
        exam_json = exam.get_json()
        self.assertDictEqual(exam_json, {
            "id": None,  # Not set until committed to DB
            "teacher_id": 1,
            "title": "Final Exam",
            "course_code": "CS101",
            "date_created": None,  # Would be a timestamp in a real DB entry
            "saved": False,
            "questions": [],
            "statistics": []
        })

    def test_exam_saved_default(self):
        exam = Exam(teacher_id=1, title="Midterm", course_code="CS102")
        assert exam.saved is False

class OptionUnitTests(unittest.TestCase):
    def test_new_option(self):
        option = Option(questionId=1, body="Answer A", image=None, is_correct=True)
        assert option.questionId == 1
        assert option.body == "Answer A"
        assert option.image is None
        assert option.is_correct is True

    def test_get_json(self):
        option = Option(questionId=2, body="Answer B", image="image.png", is_correct=False)
        option_json = option.get_json()
        self.assertDictEqual(option_json, {
            "id": None,  # Not set until committed to DB
            "questionId": 2,
            "body": "Answer B",
            "image": "image.png",
            "is_correct": False
        })

    def test_toggle_is_correct(self):
        option = Option(questionId=3, body="Answer C", is_correct=False)
        option.toggle()
        assert option.is_correct is True
        option.toggle()
        assert option.is_correct is False


class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User(firstName='John', lastName='Doe', username='johndoe', password='password123', email='johndoe@email.com')
        assert user.firstName == 'John'
        assert user.lastName == 'Doe'
        assert user.username == 'johndoe'
        assert user.email == 'johndoe@email.com'
        assert user.check_password('password123')
        assert user.password != 'password123'  # Ensure the password is hashed

    def test_get_json(self):
        user = User(firstName='John', lastName='Doe', username='johndoe', password='password123', email='johndoe@email.com')
        user_json = user.get_json()
        self.assertDictEqual(user_json, {
            'id': None,  # Not set until committed to DB
            'firstName': 'John',
            'lastName': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@email.com'
        })

    def test_set_password(self):
        user = User(firstName='John', lastName='Doe', username='johndoe', password='password123', email='johndoe@email.com')
        hashed_password = user.password
        assert check_password_hash(hashed_password, 'password123')  # Check if the hashed password is valid

    def test_check_password(self):
        user = User(firstName='John', lastName='Doe', username='johndoe', password='password123', email='johndoe@email.com')
        assert user.check_password('password123')  # Should return True
        assert not user.check_password('wrongpassword')  # Should return False


class TagUnitTests(unittest.TestCase):

    def test_new_tag(self):
        # Create a tag instance
        tag = Tag(question_id=1, tag_text='Science')
        assert tag.tag_text == 'Science'
        assert tag.question_id == 1

    def test_get_json(self):
        # Create a tag instance and check if `get_json` returns the expected dictionary
        tag = Tag(question_id=1, tag_text='Science')
        tag_json = tag.get_json()
        self.assertDictEqual(tag_json, {
            'tag_id': None,  # Not set until committed to DB
            'tag_text': 'Science'
        })

    def test_tag_creation(self):
        # Test to ensure a tag is correctly created and its attributes set
        tag = Tag(question_id=1, tag_text='Math')
        self.assertEqual(tag.tag_text, 'Math')
        self.assertEqual(tag.question_id, 1)

    def test_tag_relationship(self):
        tag = Tag(question_id=1, tag_text='Art')
        self.assertEqual(tag.question_id, 1)


class QuestionUnitTests(unittest.TestCase):

    def test_new_question(self):
        question = Question(teacherId=1, text="What is 2+2?", difficulty="easy", courseCode="MATH101", options=[])
        
        #Options are created, associated with the question
        options = [
            Option(questionId=question.id, body="Option A", is_correct=True),
            Option(questionId=question.id, body="Option B", is_correct=False)
        ]
        
        question.options = options
        
        # Test the question options (for example)
        self.assertEqual(len(question.options), 2)
        self.assertEqual(question.options[0].body, "Option A")
        self.assertTrue(question.options[0].is_correct)


    def test_get_json(self):
        question = Question(teacherId=1, text="What is 2 + 2?", difficulty="Easy", courseCode="MATH101", options=[])
        
        options = [
            Option(questionId=question.id, body="Option A", is_correct=True),
            Option(questionId=question.id, body="Option B", is_correct=False)
        ]
        
        # Add the options to the question
        question.options = options
        
        # Get the JSON representation of the question
        question_json = question.get_json()
        
        # Check if get_json method returns correct dictionary
        self.assertEqual(question_json["text"], "What is 2 + 2?")
        self.assertEqual(question_json["difficulty"], "Easy")
        self.assertEqual(question_json["course code"], "MATH101")
        self.assertEqual(len(question_json["options"]), 2)  # Check if options are included

    def test_question_creation_with_options(self):
        question = Question(teacherId=1, text="What is the capital of France?", difficulty="medium", courseCode="HIST202", options=[])
        
        options = [
            Option(questionId=question.id, body="Paris", is_correct=True),
            Option(questionId=question.id, body="London", is_correct=False)
        ]
        
        question.options = options
        
        # Check that the question has the correct number of options
        self.assertEqual(len(question.options), 2)

    def test_question_relationship_with_exam(self):
        question = Question(teacherId=1, text="What is 2 + 2?", difficulty="Easy", courseCode="MATH101", options=[])
        
        # Create options and associate them with the question
        options = [
            Option(questionId=question.id, body="Option A", is_correct=True),
            Option(questionId=question.id, body="Option B", is_correct=False)
        ]
        
        # Assign the options to the question (since Question expects options to be passed)
        question.options = options
        
        # Create an exam
        exam = Exam(teacher_id=1, title="Midterm Exam", course_code="MATH101")
        
        # Add the question to the exam's exam_questions
        exam.exam_questions.append(question)
        
        # Ensure the question is correctly added to the exam's exam_questions
        self.assertIn(question, exam.exam_questions)

    def test_question_has_statistics(self):
            # Create the Question first
        question = Question(teacherId=1, text="What is 2+2?", difficulty="easy", courseCode="MATH101", options=[])
        
        # Create options and associate with question
        options = [
            Option(questionId=question.id, body="4", is_correct=True),
            Option(questionId=question.id, body="5", is_correct=False)
        ]
        
        question.options = options
        
        # Check the number of options for the question
        self.assertEqual(len(question.options), 2)

    def test_question_tag_relationship(self):
           # Create the question first with an empty list of options (or set options to an empty list)
        question = Question(teacherId=1, text="What is 2 + 2?", difficulty="Easy", courseCode="MATH101", options=[])
        
        # Create options with the question relationship
        options = [
            Option(body="Option A", is_correct=True, questionId=question.id),
            Option(body="Option B", is_correct=False, questionId=question.id)
        ]
        
        # Append options to the question
        question.options.extend(options)
        
        # Create a tag and associate it with the question
        tag = Tag(question_id=question.id, tag_text="Mathematics")
        
        # Append the tag to the question's tag relationship
        question.tag.append(tag)
        
        # Ensure that the tag is properly associated with the question
        self.assertIn(tag, question.tag)


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


# def test_authenticate():
#     user = create_user("bob", "bobpass")
#     assert login("bob", "bobpass") != None

class TeachersIntegrationTests(unittest.TestCase):
    def test_create_teacher(self):
        teacher = create_teacher("Terry", "Wu", "Terry234", "terpass", "terry@email.com")
        assert teacher.firstName == "Terry"
        assert teacher.lastName == "Wu"
        assert teacher.check_password("terpass")
        assert teacher.email == "terry@email.com"
    
    def test_get_all_teachers_json(self):
        teacher = create_teacher("Wendy", "Frey", "Wen25", "wenderpass", "wendy@email.com")
        teachers_json = get_all_teacher_json()
        self.assertListEqual([
            {'id':1,
            'firstName':"Terry",
            'lastName' :"Wu",
            'userName' : "Terry234",
            'email':"terry@email.com"}, 

            {'id':2, 
            'firstName':"Wendy",
            'lastName' :"Frey",
            'userName' : "Wen25",
            'email':"wendy@email.com"}
            ], teachers_json)

    def test_update_teacher(self):
        update_teacher(2, "WenWarrior", "Wen@email.com")
        teacher = get_teacher(2)
        assert teacher.username == "WenWarrior"
        assert teacher.email == "Wen@email.com"





# class UsersIntegrationTests(unittest.TestCase):

#     def test_create_user(self):
#         user = create_user("rick", "bobpass")
#         assert user.username == "rick"

#     def test_get_all_users_json(self):
#         users_json = get_all_users_json()
#         self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

#     # Tests data changes in the database
#     def test_update_user(self):
#         update_user(1, "ronnie")
#         user = get_user(1)
#         assert user.username == "ronnie"
        

