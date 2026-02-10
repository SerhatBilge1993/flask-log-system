from flask import Blueprint, render_template, request, flash, jsonify, current_app as app
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  
            db.session.add(new_note) 
            db.session.commit()
            app.logger.info(f"Note created by user {current_user.id}: {note[:30]}")
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)  
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            app.logger.warning(f"Note deleted by user {current_user.id}: ID {noteId}")

    return jsonify({})


@views.route("/logs")
@login_required
def logs():
    log_path = "instance/app.log"

    try:
        with open(log_path, "r", encoding="utf8") as f:
            content = f.readlines()
    except FileNotFoundError:
        content = ["Log file not found.\n"]

    return render_template("logs.html", lines=reversed(content), user=current_user)

