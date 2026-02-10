from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from . import log_event

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            log_event(current_user.get_id(), "Created note", "SUCCESS")
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            log_event(current_user.get_id(), f"Deleted note {noteId}", "WARNING")

    return jsonify({})



@views.route('/logs')
@login_required
def logs():
    from .models import Log

    page = request.args.get('page', 1, type=int)
    level_filter = request.args.get('level', None)
    search = request.args.get('search', "")
    date_from = request.args.get('from', "")
    date_to = request.args.get('to', "")

    query = Log.query.filter_by(user_id=current_user.id)

    if level_filter:
        query = query.filter(Log.level == level_filter.upper())

    if search:
        query = query.filter(Log.action.ilike(f"%{search}%"))

    if date_from:
        query = query.filter(Log.time >= date_from)
    if date_to:
        query = query.filter(Log.time <= date_to)

    logs = query.order_by(Log.time.desc()).paginate(page=page, per_page=10)

    return render_template(
        "logs.html",
        user=current_user,
        logs=logs,
        level_filter=level_filter,
        search=search,
        date_from=date_from,
        date_to=date_to
    )



@views.route('/api/log', methods=['POST'])
def api_log():
    data = request.get_json()

    if data.get("key") != "YOUR_SECRET_API_KEY":
        return jsonify({"error": "unauthorized"}), 401

    log_event(
        user_id=data.get("user_id", None),
        action=data.get("message", "No message"),
        level=data.get("level", "INFO")
    )

    return jsonify({"status": "logged"})


@views.route('/dashboard')
@login_required
def dashboard():
    from .models import Log

    logs = Log.query.filter_by(user_id=current_user.id).all()

    level_stats = {}
    for log in logs:
        level_stats[log.level] = level_stats.get(log.level, 0) + 1

    per_day = {}
    for log in logs:
        d = log.time.strftime("%Y-%m-%d")
        per_day[d] = per_day.get(d, 0) + 1

    return render_template(
        "dashboard.html",
        user=current_user,
        level_stats=level_stats,
        per_day=per_day
    )
