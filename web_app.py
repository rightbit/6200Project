#!/usr/bin/env python3
"""
Better Jira Generator - Web Application
A web interface for the Better Jira Generator chatbot.
"""

import json
import os
import hashlib
import secrets
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
    session,
)
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-for-local-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

DATA_EXPORTS_PATH = Path('data_exports.json')
SAVED_SESSION_PATH = Path('saved_session.json')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


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
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='exports')


def generate_salt():
    """Generate a random salt for password hashing."""
    return secrets.token_hex(32)


def hash_password(password, salt):
    """Hash a password with SHA-256 and salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password, salt, stored_hash):
    """Verify a password against stored hash."""
    return hash_password(password, salt) == stored_hash


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
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
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

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
    """Migrate existing data_exports.json to database and create demo users."""
    with app.app_context():
        try:
            # Create demo users if they don't exist
            demo_pm = User.query.filter_by(username='demo-pm').first()
            if not demo_pm:
                salt = generate_salt()
                password_hash = hash_password('demo', salt)
                demo_pm = User(
                    username='demo-pm',
                    password_hash=password_hash,
                    salt=salt
                )
                db.session.add(demo_pm)

            demo_dev = User.query.filter_by(username='demo-dev').first()
            if not demo_dev:
                salt = generate_salt()
                password_hash = hash_password('demo', salt)
                demo_dev = User(
                    username='demo-dev',
                    password_hash=password_hash,
                    salt=salt
                )
                db.session.add(demo_dev)

            db.session.commit()

            # Get the demo-pm user ID for assigning existing exports
            demo_pm = User.query.filter_by(username='demo-pm').first()
            if not demo_pm:
                return

            # Migrate existing exports if data_exports.json exists
            if DATA_EXPORTS_PATH.exists():
                try:
                    with open(DATA_EXPORTS_PATH, 'r') as f:
                        data = json.load(f)
                except Exception:
                    return

                exports = data.get('exports', [])

                for item in exports:
                    # Use a try-except for each item to handle potential schema issues
                    try:
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
                            is_deleted=False,
                            deleted_at=None,
                            user_id=demo_pm.id,  # Assign to demo-pm user
                        )
                        db.session.add(export_record)
                    except Exception as e:
                        # Skip items that cause errors
                        continue

                db.session.commit()
        except Exception:
            # If migration fails, just skip it - the tables will still be created
            db.session.rollback()
            return


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
    """Fetch valid history entries from database where file_path exists and not deleted, for current user."""
    with app.app_context():
        user_id = session.get('user_id')
        if not user_id:
            return []

        exports = Export.query.filter_by(user_id=user_id, is_deleted=False).all()
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))

        # Check if username already exists
        with app.app_context():
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
                return redirect(url_for('register'))

            # Create new user
            salt = generate_salt()
            password_hash = hash_password(password, salt)

            new_user = User(
                username=username,
                password_hash=password_hash,
                salt=salt
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('login'))

        # Find user and verify password
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if user and verify_password(password, user.salt, user.password_hash):
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('items'))
            else:
                flash('Invalid username or password.', 'error')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/items')
@login_required
def items():
    with app.app_context():
        exports = Export.query.filter_by(user_id=session['user_id'], is_deleted=False).all()
        history_count = len(get_history_entries())
        return render_template('items.html', exports=exports, history_count=history_count)


@app.route('/saved_sessions', methods=['GET'])
@login_required
def saved_sessions():
    session_data = load_session_data()
    sessions = get_saved_sessions(session_data)
    messages = get_flashed_messages(with_categories=True)
    return render_template('saved_sessions.html', sessions=sessions, messages=messages)


@app.route('/saved_sessions', methods=['POST'])
@login_required
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
        user_id=session['user_id'],
    )

    with app.app_context():
        db.session.add(new_export)
        db.session.commit()

    flash('Session choice saved. Redirecting to chat.', 'success')
    return redirect(url_for('chat'))


@app.route('/chat', methods=['GET'])
@login_required
def chat():
    session_data = load_session_data()
    if not session_data or (not session_data.get('role') and session_data.get('type') != 'new_chat'):
        flash('No saved session found. Please choose a saved session or start a new chat.', 'error')
        return redirect(url_for('saved_sessions'))

    session_type = 'new' if session_data.get('type') == 'new_chat' else 'resume'
    messages = get_flashed_messages(with_categories=True)
    return render_template('chat.html', session=session_data, session_type=session_type, messages=messages)


@app.route('/history', methods=['GET'])
@login_required
def history():
    entries = get_history_entries()
    messages = get_flashed_messages(with_categories=True)
    return render_template('history.html', entries=entries, messages=messages)


@app.route('/history', methods=['POST'])
@login_required
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
@login_required
def history_detail(entry_id):
    with app.app_context():
        export = Export.query.get(entry_id)
        if not export or export.is_deleted or export.user_id != session['user_id']:
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


@app.route('/items/delete/<int:export_id>', methods=['POST'])
@login_required
def delete_export(export_id):
    """Soft delete an export record."""
    with app.app_context():
        export = Export.query.get(export_id)
        if not export or export.user_id != session['user_id']:
            flash('Export item not found.', 'error')
            return redirect(url_for('items'))

        if export.is_deleted:
            flash('This item has already been deleted.', 'warning')
            return redirect(url_for('items'))

        # Mark as deleted
        export.is_deleted = True
        export.deleted_at = datetime.utcnow()
        db.session.commit()

        flash(f'Successfully deleted: {export.filename}', 'success')
        return redirect(url_for('items'))


@app.route('/history/update/<int:export_id>', methods=['POST'])
@login_required
def update_export(export_id):
    """Continue chat and update the export file with AI-generated content."""
    with app.app_context():
        export = Export.query.get(export_id)
        if not export or export.is_deleted or export.user_id != session['user_id']:
            flash('Export item not found.', 'error')
            return redirect(url_for('history'))

        file_path = export.file_path or ''
        if not file_path or not Path(file_path).exists():
            flash('The associated file is missing or unavailable.', 'error')
            return redirect(url_for('history'))

        # Get user message from form
        user_message = request.form.get('chat_message', '').strip()
        if not user_message:
            flash('Please enter a message.', 'warning')
            return redirect(url_for('history_detail', entry_id=export_id))

        # Read current file content
        try:
            with open(file_path, 'r') as f:
                current_content = f.read()
        except Exception as e:
            flash(f'Could not read file: {e}', 'error')
            return redirect(url_for('history_detail', entry_id=export_id))

        # Call AI helper to update content
        try:
            from main import get_groq_client, update_markdown_with_ai
            client = get_groq_client()
            updated_content = update_markdown_with_ai(
                client,
                current_content,
                user_message,
                export.user_type or 'Developer',
                export.repository or ''
            )

            # Save updated content back to file
            with open(file_path, 'w') as f:
                f.write(updated_content)

            flash('Successfully updated the file with AI response!', 'success')
            return redirect(url_for('history_detail', entry_id=export_id))

        except ImportError:
            flash('AI service not available. Please check your configuration.', 'error')
            return redirect(url_for('history_detail', entry_id=export_id))
        except Exception as e:
            flash(f'Error updating file: {e}', 'error')
            return redirect(url_for('history_detail', entry_id=export_id))


@app.route('/new_chat', methods=['GET'])
@login_required
def new_chat():
    """Display form to start a new chat."""
    return render_template('new_chat.html', username=session.get('username'))


@app.route('/new_chat', methods=['POST'])
@login_required
def create_new_chat():
    """Create a new chat with GitHub repo and project description."""
    with app.app_context():
        repo_url = request.form.get('repo_url', '').strip()
        project_description = request.form.get('project_description', '').strip()
        user_type = request.form.get('user_type', 'Developer').strip()
        
        if not repo_url:
            flash('Please provide a GitHub repository URL.', 'error')
            return redirect(url_for('new_chat'))
        
        if not project_description:
            flash('Please provide a project description.', 'error')
            return redirect(url_for('new_chat'))
        
        try:
            from main import get_groq_client
            client = get_groq_client()
            
            system_prompt = f"""You are an AI assistant helping create Jira task descriptions.

The codebase is at: {repo_url}
User role: {user_type}

Your task:
1. Review the project description provided by the user
2. Create a comprehensive, well-structured markdown document outlining the project
3. Include sections for:
   - Project Overview
   - Goals and Objectives
   - Key Features
   - Technical Requirements
   - Success Criteria
4. Format the document professionally with proper markdown syntax
5. Return ONLY the markdown content (no explanations or extra text)

Be thorough, professional, and focus on clarity and completeness."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""Based on this project description, please create a comprehensive markdown document outlining the project:

---PROJECT DESCRIPTION---
{project_description}

Please return the formatted markdown document."""
                }
            ]
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            
            ai_generated_content = response.choices[0].message.content
            
            filename = f"project_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = str(Path('exports') / filename)
            
            Path('exports').mkdir(exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(ai_generated_content)
            
            export = Export(
                filename=filename,
                original_name=f"Project for {repo_url.split('/')[-1]}",
                user_type=user_type,
                repository=repo_url,
                file_path=file_path,
                action='new_chat',
                user_id=session['user_id'],
                is_deleted=False
            )
            
            db.session.add(export)
            db.session.commit()
            
            flash('Successfully created new chat and generated project outline!', 'success')
            return redirect(url_for('history_detail', entry_id=export.id))
            
        except ImportError:
            flash('AI service not available. Please check your configuration.', 'error')
            return redirect(url_for('new_chat'))
        except Exception as e:
            flash(f'Error creating new chat: {e}', 'error')
            return redirect(url_for('new_chat'))


if __name__ == '__main__':
    init_db()
    migrate_json_to_db()
    app.run(debug=True, host='127.0.0.1', port=8080)
