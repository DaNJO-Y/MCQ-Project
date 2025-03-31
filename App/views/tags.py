from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from flask_login import login_user, login_required, logout_user, current_user
from.index import index_views
from App.models import *

from App.controllers import *
import json
from.index import index_views
from .auth import auth_views

tags_views = Blueprint('tags_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    

@tags_views.route('/tags',methods=['GET'])
def tagsPage():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)

@tags_views.route('/editTags/<int:question_id>',methods=['GET'])
@login_required
def editTagsPage(question_id):
    tags = Tag.query.all()
    question = get_question(question_id)
    if not question:
        flash('Question not found')
        return jsonify({"error": "No question data"}), 400
    user = current_user
    teacher = get_teacher(user.id)
    if not teacher:
        flash('Teacher is not logged in.')
        return jsonify({"error": "Not teacher data"}), 400
    chosenQuestion = ""
    for q in teacher.questions:
        if q.id == question.id:
            chosenQuestion = q
    return render_template('editTags.html', tags=tags, question=chosenQuestion)

@tags_views.route('/create_tag', methods=['POST'])
def createTag():
    data = request.get_json()
    tag_text = data.get('tag_text')
    question_id = data.get('question_id')
    print(question_id)
    print(tag_text)
    if not tag_text or not question_id:
        return jsonify({'error': 'Missing tag text or question ID'}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    # Check if the tag already exists (optional)
    existing_tag = Tag.query.filter_by(tag_text=tag_text).first()
    if existing_tag:
        return jsonify({'message': 'Tag already exists for this question', 'tag_text': existing_tag.tag_text, 'id': existing_tag.id}), 200
    else:
        new_tag = Tag(question_id=question_id, tag_text=tag_text)
        db.session.add(new_tag)
        db.session.commit()

        print(new_tag.get_json())
        return jsonify({'message': 'Tag created successfully', 'tag_text': new_tag.tag_text, 'id': new_tag.id}), 201

@tags_views.route('/associate_tags', methods=['POST'])
def append_tag():
    data = request.get_json()
    question_id = data.get('question_id')
    tag_ids = data.get('tag_ids')

    if not question_id or not tag_ids:
        return jsonify({'error': 'Missing question_id or tag_ids'}), 400
    
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag:
            if tag not in question.tag:
                question.tag.append(tag)

    db.session.add(question)
    db.session.commit()
    print(question.tag)
    return jsonify({'message': 'Tag created and associated successfully'}), 200

@tags_views.route('/disassociate_tags', methods=['POST'])
def un_append_tag():
    data = request.get_json()
    question_id = data.get('question_id')
    tag_ids = data.get('tag_ids')

    if not question_id or not tag_ids:
        return jsonify({'error': 'Missing question_id or tag_ids'}), 400
    
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    question.tag.clear()
    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag:
            if tag not in question.tag:
                question.tag.append(tag)

    db.session.add(question)
    db.session.commit()
    print(question.tag)
    return jsonify({'message': 'Tag associated successfully'}), 200

