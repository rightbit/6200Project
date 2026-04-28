#!/usr/bin/env python3
"""
Better Jira Generator - Web Application
A web interface for the Better Jira Generator chatbot.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-for-local-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

DATA_EXPORTS_PATH = Path('data_exports.json')
SAVED_SESSION_PATH = Path('saved_session.json')


class Export(db.Model):
    __tablename__ = 'exports'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_type = db.Column(db.String(100))
    repository = db.Column(db.String(500))
    file_path = db.Column(db.String(1024))
    action = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'date': self.date.isoformat() if self.date else None,
            'user_type': self.user_type,
            'repository': self.repository,
            'file_path': self.file_path,
            'action': self.action,
        }


def init_db():
    """Initialize database tables."""
    with app.app_context():
        db.create_all()


def migrate_json_to_db():
    """Migrate existing data_exports.json to database."""
    if not DATA_EXPORTS_PATH.exists():
        return

    try:
        with open(DATA_EXPORTS_PATH, 'r') as f:
            data = json.load(f)
    except Exception:
        return

    exports = data.get('exports', [])

    with app.app_context():
        for item in exports:
            existing = Export.query.filter_by(filename=item.get('filename')).first()
            if existing:
                continue

            export_record = Export(
                filename=item.get('filename', ''),
                original_name=item.get('original_name'),
                date=datetime.fromisoformat(item['date']) if item.get('date') else datetime.utcnow(),
                user_type=item.get('user_type'),
                repository=item.get('repository'),
                file_path=item.get('file_path'),
                action=item.get('action'),
            )
            db.session.add(export_record)

        db.session.commit()


def load_json_file(path, default):
    if not path.exists():
        return default

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return default


def save_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_session_data():
    return load_json_file(SAVED_SESSION_PATH, {})


def save_session_data(data):
    save_json_file(SAVED_SESSION_PATH, data)


def get_saved_sessions(session_data):
    sessions = session_data.get('sessions')
    if isinstance(sessions, list) and sessions:
        return sessions

    if session_data.get('role'):
        return [session_data]

    return []


def get_history_entries():
    """Fetch valid history entries from database where file_path exists."""
    with app.app_context():
        exports = Export.query.all()
        valid_entries = []
        for export in exports:
            file_path = export.file_path or ''
            if file_path and Path(file_path).exists():
                valid_entries.append({
                    'id': export.id,
                    'filename': export.filename,
                    'file_path': export.file_path,
                    'original_name': export.original_name or '',
                    'date': export.date.isoformat() if export.date else '',
                    'repository': export.repository or '',
                    'user_type': export.user_type or '',
                })
        return valid_entries


@app.route('/')
@app.route('/items')
def items():
    with app.app_context():
        exports = Export.query.all()
        history_count = len(get_history_entries())
        return render_template('items.html', exports=exports, history_count=history_count)


@app.route('/saved_sessions', methods=['GET'])
def saved_sessions():
    session_data = load_session_data()
    sessions = get_saved_sessions(session_data)
    messages = get_flashed_messages(with_categories=True)
    return render_template('saved_sessions.html', sessions=sessions, messages=messages)


@app.route('/saved_sessions', methods=['POST'])
def choose_saved_session():
    session_data = load_session_data()
    sessions = get_saved_sessions(session_data)
    choice = request.form.get('selection', 'new_chat')

    if choice == 'new_chat':
        selected = {
            'role': '',
            'repository': '',
            'file_info': None,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'new_chat',
        }
        action = 'new_chat'
    else:
        try:
            index = int(choice)
            selected = sessions[index]
            selected = {**selected}
            selected['timestamp'] = datetime.utcnow().isoformat()
            selected['type'] = 'saved_session'
            action = 'resume_saved_session'
        except (ValueError, IndexError):
            flash('Invalid session selection. Please try again.', 'error')
            return redirect(url_for('saved_sessions'))

    updated_session = {
        **selected,
        'sessions': sessions,
    }

    save_session_data(updated_session)

    filename = f'session-{action}-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.json'
    new_export = Export(
        filename=filename,
        original_name=selected.get('repository', 'new_chat'),
        user_type=selected.get('role', 'New Chat'),
        repository=selected.get('repository', ''),
        file_path=selected.get('file_info', {}).get('file_path', '') if isinstance(selected.get('file_info'), dict) else '',
        action=action,
    )

    with app.app_context():
        db.session.add(new_export)
        db.session.commit()

    flash('Session choice saved. Redirecting to chat.', 'success')
    return redirect(url_for('chat'))


@app.route('/chat', methods=['GET'])
def chat():
    session_data = load_session_data()
    if not session_data or (not session_data.get('role') and session_data.get('type') != 'new_chat'):
        flash('No saved session found. Please choose a saved session or start a new chat.', 'error')
        return redirect(url_for('saved_sessions'))

    session_type = 'new' if session_data.get('type') == 'new_chat' else 'resume'
    messages = get_flashed_messages(with_categories=True)
    return render_template('chat.html', session=session_data, session_type=session_type, messages=messages)


@app.route('/history', methods=['GET'])
def history():
    entries = get_history_entries()
    messages = get_flashed_messages(with_categories=True)
    return render_template('history.html', entries=entries, messages=messages)


@app.route('/history', methods=['POST'])
def choose_history_entry():
    entries = get_history_entries()
    choice = request.form.get('selection')

    try:
        selected_id = int(choice)
    except (ValueError, TypeError):
        flash('Invalid selection. Please choose a valid history item.', 'error')
        return redirect(url_for('history'))

    valid_ids = [entry['id'] for entry in entries]
    if selected_id not in valid_ids:
        flash('That file entry does not exist or is unavailable.', 'error')
        return redirect(url_for('history'))

    return redirect(url_for('history_detail', entry_id=selected_id))


@app.route('/history/view/<int:entry_id>', methods=['GET'])
def history_detail(entry_id):
    with app.app_context():
        export = Export.query.get(entry_id)
        if not export:
            flash('History item not found.', 'error')
            return redirect(url_for('history'))

        file_path = export.file_path or ''
        if not file_path or not Path(file_path).exists():
            flash('The selected history file is missing or unavailable.', 'error')
            return redirect(url_for('history'))

        try:
            with open(file_path, 'r') as f:
                contents = f.read()
        except Exception as e:
            flash(f'Unable to read file: {e}', 'error')
            return redirect(url_for('history'))

        return render_template('history_detail.html', entry=export, contents=contents)


if __name__ == '__main__':
    init_db()
    migrate_json_to_db()
    app.run(debug=True, host='127.0.0.1', port=8080)
