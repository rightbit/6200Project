# Better Jira Generator
**INFO-6200 Spring Class Project**

## General Vision and Goal
The goal of this program is to create a chatbot that will help product managers write better descriptions of their requirements, help developers find the area of code to work in, and finally create a test plan for the task.

## Requirements

- Python 3.8 or higher
- Groq API key (free tier available)
- Internet connection

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd 6200Project
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
   * May need to run `pip3` or `python3 -m pip` instead

4. **Set up your environment file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Get your free Groq API key from [https://console.groq.com](https://console.groq.com)
   - Open `.env` and replace the placeholder values with your actual configuration:
     ```
     GROQ_API_KEY=gsk_your_actual_key_here
     FLASK_SECRET_KEY=your-secure-secret-key-at-least-32-chars
     SAVE_FOLDER_PATH=exports
     ```

## Database Setup

The application uses **SQLite** for data persistence.

When you run `web_app.py` for the first time:
1. A new SQLite database file (`app.db`) will be created automatically.
2. All database tables will be initialized.
3. Demo user accounts will be created.
4. If a `data_exports.json` file exists, its data will be automatically migrated to the database.

If you need to manually migrate data from `data_exports.json`, run:
```bash
python migrate_json_to_db.py
```

The database stores all export records and is the primary data source for the web interface.

## Environment Variables

The application uses the following environment variables (configured in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | `change-this-for-local-testing` |
| `FLASK_ENV` | Flask environment (`development` or `production`) | `development` |
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` |
| `SAVE_FOLDER_PATH` | Folder for saving export files | `exports` |
| `GROQ_API_KEY` | Groq API key for AI functionality | *Required* |
| `AI_MODEL` | AI model to use | `llama3-8b-8192` |
| `AI_API_BASE_URL` | AI API base URL | `https://api.groq.com` |

## Final Submission Checklist

Before submitting your project, ensure:

- ✅ `requirements.txt` exists with all dependencies
- ✅ `.env.example` exists with all required variables
- ✅ `.env` is NOT committed to Git (contains sensitive data)
- ✅ `.gitignore` excludes sensitive and generated files
- ✅ README documents all routes and setup instructions
- ✅ README explains demo accounts (`demo-pm`/`demo`, `demo-dev`/`demo`)
- ✅ All configuration comes from environment variables
- ✅ App runs with `python web_app.py` (development)
- ✅ App runs with `gunicorn web_app:app` (production)
- ✅ Database migrations run successfully on startup
- ✅ Authentication protects all routes except login/register
- ✅ API routes return proper JSON responses
- ✅ Users can only access their own exports
- ✅ Project folder is ready to zip for submission

## Running the Program

### Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Initialize database:**
   ```bash
   python web_app.py  # This will create tables and migrate data
   ```

### Command Line Interface (CLI)

Run the main application:
```bash
python main.py
```

### Web Interface

**Development server:**
```bash
python web_app.py
```

**Production server (WSGI):**
```bash
gunicorn web_app:app --bind 0.0.0.0:8000
```

Then open your web browser and navigate to:
```
http://localhost:8080/
```

### Demo Accounts

The application includes two demo accounts for testing:

- **Project Manager:** `demo-pm` / `demo`
- **Developer:** `demo-dev` / `demo`

Use these accounts to explore all features without creating your own account.

## Available Routes

### Authentication Routes
- `GET  /register` - User registration form
- `POST /register` - Process user registration
- `GET  /login` - User login form
- `POST /login` - Process user login
- `GET  /logout` - User logout

### Main Application Routes
- `GET  /` - Redirects to `/items` (requires login)
- `GET  /items` - List all user's export items (requires login)
- `GET  /saved_sessions` - Session selection form (requires login)
- `POST /saved_sessions` - Process session selection (requires login)
- `GET  /chat` - Chat interface (requires login)
- `GET  /history` - List export history (requires login)
- `POST /history` - Choose history entry (requires login)
- `GET  /history/view/<export_id>` - View export details (requires login)
- `POST /history/update/<export_id>` - Update export with AI (requires login)
- `POST /items/delete/<export_id>` - Soft delete export (requires login)
- `GET  /new_chat` - Start new chat form (requires login)
- `POST /new_chat` - Create new chat with AI (requires login)

### API Routes (JSON)
- `GET  /api/v1/items` - Get all user's export items as JSON (requires login)
- `GET  /api/v1/items/<item_id>` - Get specific export item as JSON (requires login)

### Static Files
- `/static/*` - CSS, JavaScript, and other static assets

To inspect file-backed exports, use:
```
http://localhost:8080/history
```

or

```
http://127.0.0.1:8080/history
```

Use the history page to choose an available export by filename and view the contents of the referenced file.

**Note:** Port 8080 is used instead of 5000 to avoid conflicts with macOS AirPlay Receiver.

To stop the web server, press `Ctrl+C` in the terminal.

### Session Persistence

The application automatically saves your session (role, repository, task file) to `saved_session.json`. When you restart the program:
- If a previous session exists, you'll be asked if you want to continue from where you left off
- Choose **Yes** to resume with your previous settings
- Choose **No** to start fresh (clears the saved session)

## Usage

1. **Select your role:**
   - Choose `1` for Product Manager (focus on feature requirements)
   - Choose `2` for Developer (focus on implementation)

2. **Upload a task description file (optional):**
   - When prompted, choose `y` to upload a file or `n` to skip
   - Supported formats: PDF, TXT, DOC/DOCX
   - Enter the file path (supports `~` for home directory)
   - Example: `~/Documents/requirements.pdf`
   - The file content will be included in the AI's context

3. **Provide a GitHub repository URL:**
   - Enter the URL of the codebase you're working with
   - (Full repo analysis coming in future versions)

4. **Chat with the assistant:**
   - Ask questions about features, requirements, or implementation
   - The AI will provide context-aware assistance based on your role
   - Use the commands below to manage your chat sessions

### Commands During Chat

- **`NEW`** - Start a new chat session
  - Clears current conversation
  - Clears saved session data
- **`SAVE`** - Save the current chat to a markdown file
  - Prompts for a filename
  - Saves to your configured save folder
  - Registers the export in chat history
- **`HISTORY`** - View all previously saved chats
  - Shows filename, date, role, and repository
- **`OPEN`** - Open and continue a previously saved chat
  - Select from your chat history
  - Loads all previous messages
  - Continue the conversation where you left off
- **`LIST`** - Display all loaded resources:
  - Your current role
  - GitHub repository URL
  - Task file details (name, path, type, size)
  - Save folder location
  - Number of messages in current chat
- **`HELP`** - Show all available commands
- **`EXIT`** - Quit the program

### Web Interface - Managing Exports (Chunk 8)

The web interface at `/items` displays all saved exports with action buttons:

- **View:** Opens the export file and displays its contents
- **Update:** Continues a conversation with AI to refine the markdown content
- **Delete:** Marks the export as deleted (soft delete - data is preserved, not removed)

When you click **Update**, you'll be taken to the history detail page where you can:
1. Review the current markdown content
2. Enter a message in the "Continue Chat" form
3. Click "Send & Update File" to send your message to the AI
4. The AI will refine the content based on your feedback
5. The updated markdown is automatically saved to the file
6. You'll be redirected back to see the updated content

**Important:** Deleted exports are hidden from normal views but their data remains in the database. To permanently remove data, contact your system administrator.

### API Endpoints (Chunk 10)

The application provides a REST API for programmatic access to export data. All API endpoints require authentication.

#### Authentication
All API endpoints require a logged-in user session. Make requests to web endpoints first to establish authentication, or implement session-based authentication in your API client.

#### Endpoints

**GET /api/v1/items**
Returns a JSON array of all export items owned by the authenticated user.

Example request:
```bash
curl -X GET http://localhost:8080/api/v1/items \
  -H "Cookie: session=<your-session-cookie>"
```

Example response:
```json
{
  "items": [
    {
      "id": 1,
      "filename": "jira_export.md",
      "original_name": null,
      "date": "2026-04-28T14:30:00",
      "user_type": "Product Manager",
      "repository": "https://github.com/example/repo",
      "file_path": "exports/jira_export.md",
      "action": "new_chat",
      "created_at": "2026-04-28T14:30:00"
    }
  ]
}
```

**GET /api/v1/items/{item_id}**
Returns a single export item by ID, if owned by the authenticated user.

Example request:
```bash
curl -X GET http://localhost:8080/api/v1/items/1 \
  -H "Cookie: session=<your-session-cookie>"
```

Example response (success):
```json
{
  "id": 1,
  "filename": "jira_export.md",
  "original_name": null,
  "date": "2026-04-28T14:30:00",
  "user_type": "Product Manager",
  "repository": "https://github.com/example/repo",
  "file_path": "exports/jira_export.md",
  "action": "new_chat",
  "created_at": "2026-04-28T14:30:00"
}
```

Example response (not found):
```json
{
  "error": "Item not found"
}
```
Status: 404 Not Found

#### Error Responses

- **401 Unauthorized**: Returned when user is not authenticated
  ```json
  {
    "error": "Authentication required"
  }
  ```

- **404 Not Found**: Returned when item doesn't exist or user doesn't own it
  ```json
  {
    "error": "Item not found"
  }
  ```

#### Notes
- All responses are JSON-formatted
- Deleted items are automatically excluded from API responses
- Users can only access items they own
- Timestamps are in ISO 8601 format

### Saved Chat Files

Chat exports are saved as markdown files (.md) that can be:
- Copied directly into Jira descriptions or comments
- Opened in any text editor or markdown viewer
- Used as reference for future tasks
- Continued later using the `OPEN` command

Files are saved with a timestamp to prevent overwriting and are tracked in `data_exports.json` for easy retrieval.

## Features (Current - Chunk 4)

✅ **Web Interface:**
  - Basic Flask web application
  - Home route with "Hello Web!" message
  - HTML/CSS boilerplate for future pages
  - Local development server support

✅ **Session Management:**
  - Automatic session persistence between runs
  - Resume from last session on startup
  - Session data stored in `saved_session.json`
  - Clear session with NEW command

✅ **Enhanced Chat Interface:**
  - HELP command to view all available commands
  - Role-based chat (Product Manager or Developer)
  - Integration with Groq LLM (using Llama 3.1)

✅ **File & Resource Management:**
  - File upload support (PDF, TXT, DOC/DOCX) for task descriptions
  - Save chats as markdown files for Jira
  - Chat history tracking with metadata (`data_exports.json`)
  - Resume previous conversations with OPEN
  - Configurable save folder with auto-creation

✅ **Core Commands:**
  - NEW, SAVE, HISTORY, OPEN, LIST, HELP, EXIT
  - Conversation history maintained throughout session
  - Error handling for missing environment configuration  

✅ **Edit, Delete & AI Chat Continuation (Chunk 8):**
  - **Soft Delete:** Delete export records without losing data (marked as deleted but preserved)
  - **Update Exports:** Edit and enhance saved exports using AI chat continuation
  - **Web Interface Actions:** View, Update, and Delete buttons for each export
  - **Delete Confirmation:** JavaScript confirmation dialog prevents accidental deletions
  - **AI-Powered Updates:** Continue conversations with AI to refine markdown content
  - **File Persistence:** Updated content is saved directly to the associated markdown file
  - **Soft Delete Filtering:** Deleted records are hidden from all list views and history
  - **Database Integration:** Soft delete fields (`is_deleted`, `deleted_at`) added to Export model  

## Project Structure

```
6200Project/
├── main.py              # Main CLI application
├── web_app.py           # Web interface (Flask)
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your API keys (not committed to git)
├── data_exports.json   # Chat history metadata
├── saved_session.json  # Session persistence (auto-created)
├── test_chunk3.py      # Test script for session management
├── README.md           # This file
├── project_plan.md     # Detailed project planning
└── LICENSE
```

## Troubleshooting

**Error: .env file not found**
- Make sure you've created a `.env` file in the project root
- Copy from `.env.example` if needed

**Error: GROQ_API_KEY not configured**
- Check that your `.env` file contains a valid API key
- Get a free key from [https://console.groq.com](https://console.groq.com)

**API errors**
- Verify your internet connection
- Check that your API key is valid and active
- Ensure you haven't exceeded the free tier limits

## Future Enhancements

- Full GitHub repository indexing and analysis
- Database integration (MySQL)
- Web UI (HTML/CSS)
- QA test plan generation
- User authentication
- Deployment to Heroku