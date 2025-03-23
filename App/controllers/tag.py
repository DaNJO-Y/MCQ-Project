from App.models import Tag
from App.models import Question_Tag_Bridge
from App.models import Question
from App.database import db


def add_tag(tag_id, question_id,tag_text):
    # Check if question exists
    question = Question.query.get(question_id)
    if not question:
        return {"error": "Question not found"}

    # If tag_id is provided, fetch the tag
    if tag_id is not None:
        tag = Tag.query.get(tag_id)
        if not tag:
            return {"error": "Tag not found"}
    else:
        # If no tag_id, create a new tag 
        tag = Tag(question_id,tag_text)  #
        db.session.add(tag)
        db.session.commit()

    # Create the association
    association = Question_Tag_Bridge.insert().values(tag_id=tag.id, question_id=question.id)
    db.session.execute(association)
    db.session.commit()

    return {"message": "Tag added successfully"}




# def removeTag(){

#     #check to see if the tag exists
#     #if it exists delete the tag
#     #if it doesnt exist show a message that the tag cannot be deleted
#     #if it is deleted we need to delete the association with it 
# }

# def editTag(tag_id, new_text){
#     #check to see if the tag id exists
#     #if it exists edit the tag with the new tag text
#     #if it doesn't exist return an error to the user.
# }


