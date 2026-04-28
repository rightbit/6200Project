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

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-for-local-testing')

DATA_EXPORTS_PATH = Path('data_exports.json')
SAVED_SESSION_PATH = Path('saved_session.json')


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


def load_exports_data():
    return load_json_file(DATA_EXPORTS_PATH, {'exports': []})


def save_exports_data(data):
    save_json_file(DATA_EXPORTS_PATH, data)


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


@app.route('/')
def home():
    return redirect(url_for('saved_sessions'))


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

    exports_data = load_exports_data()
    exports_data.setdefault('exports', []).append({
        'filename': f'session-{action}-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.json',
        'original_name': selected.get('repository', 'new_chat'),
        'date': datetime.utcnow().isoformat(),
        'user_type': selected.get('role', 'New Chat'),
        'repository': selected.get('repository', ''),
        'file_path': selected.get('file_info', {}).get('file_path', '') if isinstance(selected.get('file_info'), dict) else '',
        'action': action,
    })
    save_exports_data(exports_data)

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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
