import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *
from datetime import datetime
from pytest import approx

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
            # "date_created": None,  # Would be a timestamp in a real DB entry
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
@pytest.fixture(autouse=True, scope="class")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    # db.session.remove()
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


class ExamIntegrationTests(unittest.TestCase):
    def test_create_exam(self):
        teacher_rich = create_teacher("Richard", "Williams", "Richy", "richpass", "richard23@my.gmail.com")
        questions_list = []
        
        options_list=[]
        question = save_question(teacherId=teacher_rich.id, text="What is the largest organ in the human body?", difficulty="Hard", courseCode="Integumentary system 7863",options=options_list)
        
        option_1 = create_option(question_id=question.id, body="Brain", image=None,is_correct=False)
        options_list.append(option_1)
        option_2 = create_option(question_id=question.id, body="Heart", image=None,is_correct=False)
        options_list.append(option_2)
        option_3 = create_option(question_id=question.id, body="Lungs", image=None,is_correct=False)
        options_list.append(option_3)
        option_4 = create_option(question_id=question.id, body="Skin", image=None,is_correct=True)
        options_list.append(option_4)

        question.options = options_list
        questions_list.append(question)

        options_list_2=[]
        question_2 = save_question(teacherId=teacher_rich.id, text="What is the formula for the compound that causes Hypertension?", difficulty="Medium", courseCode="BioChemistry3476",options=options_list_2)
        
        option_1 = create_option(question_id=question.id, body="H2SO4", image=None,is_correct=False)
        options_list_2.append(option_1)
        option_2 = create_option(question_id=question.id, body="H2O", image=None,is_correct=False)
        options_list_2.append(option_2)
        option_3 = create_option(question_id=question.id, body="NaCL", image=None,is_correct=True)
        options_list_2.append(option_3)
        option_4 = create_option(question_id=question.id, body="Br", image=None,is_correct=False)
        options_list_2.append(option_4)

        question_2.options = options_list_2
        questions_list.append(question_2)

        exam_statistic = ExamStatistics(1,"Mean Score: 24, Total Students answered above 50%: 200", 2022)
        exam = Exam(teacher_id=teacher_rich.id, title="Test Exam", course_code="Test4567")
        
        exam.exam_questions = questions_list
        db.session.add(exam)
        db.session.commit()

        exam = Exam.query.get(1)
        
        exam_statistic.exam_id = exam,id
        exam.statistics.append(exam_statistic)
        exam_json = get_exam_by_id(exam.id)
        assert exam_json == {
            "id": 1,
            "teacher_id": 1,
            "title": "Test Exam",
            "course_code": "Test4567",
            "saved": False,
            "questions": [1,2],
            "statistics": [{
                    "id": 1,
                    "exam_id": 1,
                    "data": "Mean Score: 24, Total Students answered above 50%: 200",
                    "year": 2022
            }]
        }

        db.session.remove()
        
        
    def test_edit_exam(self):
        teacher_rich = create_teacher("Richard", "Williams", "Richo", "richpass0", "richard45@my.gmail.com")
        questions_list = []
        
        options_list=[]
        question = save_question(teacherId=teacher_rich.id, text="Test question?", difficulty="Hard", courseCode="Test 1",options=options_list)
        
        option_1 = create_option(question_id=question.id, body="test option 1", image=None,is_correct=False)
        options_list.append(option_1)
        option_2 = create_option(question_id=question.id, body="test option 2", image=None,is_correct=False)
        options_list.append(option_2)
        option_3 = create_option(question_id=question.id, body="test option 3", image=None,is_correct=False)
        options_list.append(option_3)
        option_4 = create_option(question_id=question.id, body="test option 4", image=None,is_correct=True)
        options_list.append(option_4)

        question.options = options_list
        questions_list.append(question)

        options_list_2=[]
        question_2 = save_question(teacherId=teacher_rich.id, text="What is the formula for the compound that causes Hypertension?", difficulty="Medium", courseCode="BioChemistry3476",options=options_list_2)
        
        option_1 = create_option(question_id=question.id, body="H2SO4", image=None,is_correct=False)
        options_list_2.append(option_1)
        option_2 = create_option(question_id=question.id, body="H2O", image=None,is_correct=False)
        options_list_2.append(option_2)
        option_3 = create_option(question_id=question.id, body="NaCL", image=None,is_correct=True)
        options_list_2.append(option_3)
        option_4 = create_option(question_id=question.id, body="Br", image=None,is_correct=False)
        options_list_2.append(option_4)

        question_2.options = options_list_2
        questions_list.append(question_2)

        # exam_statistic = ExamStatistics(1,"Mean Score: 24, Total Students answered above 50%: 200", 2022)
        exam = Exam(teacher_id=teacher_rich.id, title="Test Exam for update", course_code="Test4567")
        exam.exam_questions = questions_list
        db.session.add(exam)
        db.session.commit()

        add_questions=[]
        remove_question = []
        options_list_3=[]
        question_3 = save_question(teacherId=teacher_rich.id, text="Test question", difficulty="Hard", courseCode="Test 23",options=options_list_2)
        
        option_1 = create_option(question_id=question.id, body="Test option 1", image=None,is_correct=False)
        options_list_3.append(option_1)
        option_2 = create_option(question_id=question.id, body="Test option 2", image=None,is_correct=False)
        options_list_3.append(option_2)
        option_3 = create_option(question_id=question.id, body="Test option 3", image=None,is_correct=True)
        options_list_3.append(option_3)
        option_4 = create_option(question_id=question.id, body="Test option 4", image=None,is_correct=False)
        options_list_3.append(option_4)

        question_3.options = options_list_3
        add_questions.append(question_3)
        remove_question.append(question_2)

        updated_exam_json = edit_exam(exam_id=exam.id,title="Test update",course_code="Course update",add_questions=add_questions,remove_questions=remove_question )

        assert updated_exam_json == {
            "id": 2,
            "teacher_id": 2,
            "title": "Test update",
            "course_code": "Course update",
            "saved": False,
            "questions": [3,5],
            "statistics": []
        }
        db.session.remove()
    
class OptionIntegrationTests(unittest.TestCase):
    def test_create_option(self):
        question = save_question(teacherId=2, text="Test question for options", difficulty="Intermediate", courseCode="Test 1",options=[])
        option = create_option(question_id=question.id, body="Option text", image=None, is_correct=True)
        option_json = option.get_json()
        assert option_json == {
            "id": option.id,
            "questionId":question.id,
            "body":"Option text",
            "image":None,
            "is_correct": True
        }

    def test_add_text_to_option(self):
        question = save_question(teacherId=2, text="Test question for add options", difficulty="Intermediate", courseCode="Test 1",options=[])
        option = create_option(question_id=question.id, body="", image=None, is_correct=True)
        updated_option = add_text(id=option.id, text="New text", question_id=question.id)
        option_json = updated_option.get_json()
        assert option_json == {
            "id": updated_option.id,
            "questionId":question.id,
            "body":"New text",
            "image":None,
            "is_correct": True
        }
    
    
        
    
    def test_remove_option_text(self):
        question = save_question(teacherId=2, text="Test question for remove option text", difficulty="Intermediate", courseCode="Test 1",options=[])
        option = create_option(question_id=question.id, body="Option text to be removed", image=None, is_correct=True)
        assert option.body == "Option text to be removed"
        updated_option = remove_text(id=option.id, question_id=question.id)
        option_json = updated_option.get_json()
        assert option_json == {
            "id": updated_option.id,
            "questionId":question.id,
            "body":None,
            "image":None,
            "is_correct": True
        }
    def test_toggle_is_correct(self):
        question = save_question(teacherId=2, text="Test question for option correct toggling", difficulty="Intermediate", courseCode="Test 1",options=[])
        option = create_option(question_id=question.id, body="Option text", image=None, is_correct=False)
        assert option.is_correct == False
        message = toggle_isCorrectOption(id=question.id,option_id=option.id)
        assert option.is_correct == True
        assert message["message"] == "Option is_correct toggled"

class QuestionIntegrationTests(unittest.TestCase):
    def test_save_question(self):
        question = save_question(teacherId=2,text="Test Question", difficulty="Easy", courseCode="Testing101", options=[])
        question_json = question.get_json()
        assert question_json == {
            "id": question.id,
            "teacherid": 2,
            "text": "Test Question",
            "difficulty": "Easy",
            "course code": "Testing101",
            "options": []
        }

    def test_edit_question(self):
        question = save_question(teacherId=2,text="Test Question for Editing", difficulty="Easy", courseCode="Testing1010", options=[])
        question_json = question.get_json()
        assert question_json == {
            "id": question.id,
            "teacherid": 2,
            "text": "Test Question for Editing",
            "difficulty": "Easy",
            "course code": "Testing1010",
            "options": []
        }
        updated_question = edit_question(id=question.id, text="Updated test text", difficulty="Hard", courseCode="Testing1010")
        if updated_question:
            updated_question_json = updated_question.get_json()
            assert updated_question_json == {
                "id": updated_question.id,
                "teacherid": 2,
                "text": "Updated test text",
                "difficulty": "Hard",
                "course code": "Testing1010",
                "options": []
            }
    def test_get_questions(self):
        teacher = create_teacher("Richard", "Williams", "Richo", "richpass0", "richard45@my.gmail.com")
        print("hi")
        print(teacher)
        question_1 = save_question(teacherId=teacher.id,text="Test Question 1", difficulty="Easy", courseCode="Testing101", options=[])
        question_2 = save_question(teacherId=teacher.id,text="Test Question 2", difficulty="Hard", courseCode="Testing102", options=[])
        questions_json = get_all_my_questions_json(teacher)
        self.assertListEqual([
            {'id':question_1.id,
            "teacherid": teacher.id,
            "text": "Test Question 1",
            "difficulty": "Easy",
            "course code": "Testing101",
            "options": []},

            {'id':question_2.id,
            "teacherid": teacher.id,
            "text": "Test Question 2",
            "difficulty": "Hard",
            "course code": "Testing102",
            "options": []}
            ], questions_json)

    


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
        

