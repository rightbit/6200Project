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


def get_history_entries():
    exports = load_exports_data().get('exports', [])
    valid_entries = []
    for index, entry in enumerate(exports):
        file_path = entry.get('file_path', '')
        if file_path and Path(file_path).exists():
            valid_entries.append({
                'index': index,
                'filename': entry.get('filename', '<unknown>'),
                'file_path': file_path,
                'original_name': entry.get('original_name', ''),
                'date': entry.get('date', ''),
                'repository': entry.get('repository', ''),
                'user_type': entry.get('user_type', ''),
            })
    return valid_entries


@app.route('/')
@app.route('/items')
def items():
    exports_data = load_exports_data().get('exports', [])
    history_count = len(get_history_entries())
    return render_template('items.html', exports=exports_data, history_count=history_count)


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
        selected_index = int(choice)
    except (ValueError, TypeError):
        flash('Invalid selection. Please choose a valid history item.', 'error')
        return redirect(url_for('history'))

    valid_indexes = [entry['index'] for entry in entries]
    if selected_index not in valid_indexes:
        flash('That file entry does not exist or is unavailable.', 'error')
        return redirect(url_for('history'))

    return redirect(url_for('history_detail', entry_index=selected_index))


@app.route('/history/view/<int:entry_index>', methods=['GET'])
def history_detail(entry_index):
    exports = load_exports_data().get('exports', [])
    if entry_index < 0 or entry_index >= len(exports):
        flash('History item not found.', 'error')
        return redirect(url_for('history'))

    entry = exports[entry_index]
    file_path = entry.get('file_path', '')
    if not file_path or not Path(file_path).exists():
        flash('The selected history file is missing or unavailable.', 'error')
        return redirect(url_for('history'))

    try:
        with open(file_path, 'r') as f:
            contents = f.read()
    except Exception as e:
        flash(f'Unable to read file: {e}', 'error')
        return redirect(url_for('history'))

    return render_template('history_detail.html', entry=entry, contents=contents)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
