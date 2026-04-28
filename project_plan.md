# Better Jira Generator  
**Ryan Bouche – Tech 6200 Assignment 3**

## General Instruction
This file contains the overview and project description. Each piece of the project will be implemented in chunks and tested. 

## General Vision and Goal
The goal of this program is to create a chatbot that will help product managers write better descriptions of their requirements, help developers find the area of code to work in, and finally create a test plan for the task.
(Jira is a popular issue and project tracking software. For many developers and tech managers, Jira has become a common noun for a development task, much like “Kleenex” is a common noun for a tissue, or “Google” is to do a web search.)

## Core Features
- **Product Manager:** Use a chatbot familiar with the codebase and product features to write more specific descriptions of tasks and improvements that can be handed off to a developer.
- **Developer:** Load a Jira task description into the chatbot and receive suggestions for which files are needed to make those changes in the code.
- **Developer / QA Handoff:** Transform the Jira description and proposed code changes into a set of acceptance criteria for a Quality Assurance engineer to test.

## Target Audience
- Product Managers  
- Developers  
- QA Engineers  

## Technical Stack and Architecture
- Python  
- Database: MySQL  
- Hosting: Heroku  
- Frontend: HTML / CSS  

## Non-Functional Requirements
- Users must authenticate  
- Hosted online  
- Rate and time limits on AI generation  

## Minimum Viable Product (MVP)
- AI with knowledge of the codebase and product functionality  
- UI for chat interaction and export of generated text  
- Separate functions and workflows for Product Managers and Developers  

## Nice-to-Have Features
- Ability to upload images of mockups to help describe requested changes  
- Add suggestions to QA for a test plan or Unit Tests

## Data Model: RepositoryFile
Defines a single indexed file within a repository.

- **id** (BIGINT, primary key, auto-increment) — unique record identifier  
- **path** (VARCHAR(1024), not null) — full repo-relative path (e.g., `src/api/orders/OrdersController.py`)  
- **filename** (VARCHAR(255), not null) — base filename (e.g., `OrdersController.py`)  
- **extension** (VARCHAR(20), null) — file extension (e.g., `py`, `js`, `sql`)  
- **language** (VARCHAR(50), null) — inferred programming language  
- **content_summary** (TEXT, null) — AI- or heuristic-generated summary of file purpose  
- **symbols** (JSON, null) — extracted symbols such as classes, functions, or routes  
- **last_modified_at** (DATETIME, not null) — last modified timestamp from version control  
- **indexed_at** (DATETIME, not null) — timestamp when the file was indexed by the system  

&nbsp;

# Chunk 1: CLI prototype

## Goals
Set up an api connection to a free LLM. 
Create a working prototype of the initial menu. 

## Tasks
1. Create env file and env.example with API info for a free LLM 
2. Create a command line menu that asks if the user is a product manager or a developer
    1. Error handling - Prompt user to contact the program developer if the env file does not exist
3. Ask user to link to a github repo to use as a corpus of data  
4. Create a chat with the user. 
    1. Focus the product manager chat on new features for the project
    2. Focus the developer chat on the project file structure and how to implement the feature
    3. Allow the user to use a local file (pdf, txt, doc) to describe the task
5. Keep the chat loop going , but give the user the option to type EXIT to close the program.  

## Files to create
- Main Application file
- Environment file
    - Install dependencies
- Update the Readme with requirements and instructions on running the program

## Commit the files
- Prompt to commit the files to the repo 

# Chunk 2: Saving and storing data

## Goals
Save history of chats and Save markup file to use in Jira. 

## Tasks
1. Add a save folder path to the env and env example files
    1. prompt the user at startup to add a folder path if one does not exist
2. Add a command to save the output of the chat as a markup file that can be used in a Jira description or a Comment
    1. Prompt for a filename before saving
3. Create an internal json file called data_exports.json that stores the file name, date, and user type (Manager, Developer)  
4. Refactor the command menu
    1. Add a NEW command to start a new chat
    2. Add a HISTORY command to list the saved chats
    3. Add an OPEN command to display the contents of the file and continue the chat
    4. Add a SAVE command to save the output as a markup file and register it in data_exports.json
5. Update the readme with the menu commands

## Files to create
- data_exports.json

---
# Chunk 3: Data files continued: saved_session.json 

## Goals
Save session history of last setup

## Tasks
1. At startup, If saved_session.json does not exist, create saved_session.json
2. check if saved_session.json is populated with an entry
    1. Show the contents of the saved_session file
    2. Ask if the user wants to continue from the last chat. 
    3. If the user says no, clear the contents of saved_session.json
2. Whenever user input changes regarding Role, or what entry from History, or filename, save that and other useful data to saved_session.json
3. When a user chooses NEW from the menu, clear the saved_session.json 
4. Create a HELP Command that will list the current menu commands.


## Files to create
- saved_session.json 

---
# Chunk 4: Minimal Flask implementaion

## Goals
Integrate Flask and have it respond to a web request

## Tasks
1. Install Flask for python
2. Create web_app.py and have it include Flask. 
3. Define the home route "/" 
4. Create a boilerplate head and body sections for future pages. 
5. When the user browses to the home / route Print Hello Web! in an h1 header. 
    1. The route's view funtcion must include the necessary code (within an if __name__ == "__main__" block)
6. Add instructions to the readme.md on how to launch the flask webservice locally and browse to it with localhost


## Files to create
- web_app.py


---
# Chunk 5: Saved Sessions and Chat Routing

## Goals
Build a Flask session selection flow that allows users to resume a saved session or start a new chat.

## Requirements
1. Create a Flask route `/saved_sessions` that renders an HTML form from a new `templates/` folder.
2. The form must ask the user whether they want to:
   - load a saved session, or
   - start a new chat.
3. If the user chooses a saved session, the form should display existing sessions from `saved_session.json` for selection.
4. If the user chooses New Chat, the form should allow that option and clear the chat context.
5. When the form is submitted, send the data with a POST request to a Flask route.
6. The POST route must:
   - read the user's choice from `request.form`
   - if a saved session is selected, load that session from `saved_session.json`
   - if New Chat is selected, initialize an empty session context
   - save the selected or new session context back to `saved_session.json`
   - redirect the user to a `/chat` route
7. The `/chat` route must render a page that:
   - displays the loaded session details when resuming a saved session
   - shows blank chat fields when starting a new chat
   - includes a confirmation message after redirect

## Deliverables
- Updated `web_app.py` with:
  - a GET route for `/saved_sessions` rendering a selection form
  - a POST route that processes the saved session or new chat choice
  - a `/chat` route that renders the current session context
  - JSON persistence logic for `data_exports.json` and `saved_session.json`
- A new `templates/` folder containing at least:
  - `saved_sessions.html`
  - `chat.html`

## Tasks
1. Install any required Flask template dependencies.
2. Create `templates/saved_sessions.html` with:
   - a form for choosing between saved session or new chat
   - a list of saved sessions loaded from `saved_session.json`
   - a submit button to continue to `/chat`
3. Create `templates/chat.html` with:
   - displayed session information when resuming a saved session
   - blank form fields for starting a new chat
   - a success/status message area
4. Add a GET route in `web_app.py` for `/saved_sessions`.
5. Add a POST route in `web_app.py` for `/saved_sessions` that:
   - validates the user's selection
   - loads or initializes session data
   - updates `saved_session.json`
   - redirects to `/chat`
6. Add a GET route in `web_app.py` for `/chat` that renders the selected session or new chat view.
7. Display feedback after redirecting to `/chat`.
8. Update the README with instructions for launching `/saved_sessions` and continuing to `/chat`.

## Files to create
- `web_app.py`
- `templates/saved_sessions.html`
- `templates/chat.html`
- `data_exports.json` (if not already present)
- `saved_session.json` (if not already present)

---
# Chunk 6: Data Rendering and History Lookup

## Goals
Extend the Flask app so users can view all stored export records and inspect individual saved export contents from `data_exports.json`.

## Requirements
1. Create a route `/history` that allows the user to choose an entry from `data_exports.json`.
2. This route must:
   - read and parse all data from `data_exports.json`
   - pass the full collection to a Jinja2 template for rendering
3. The Jinja2 template must use a `for` loop to iterate over the data collection and generate HTML for every item.
4. Each item should display enough details so the user can identify it by filename, date, repository, and user type.
6. The `/history` page should list only entries whose `file_path` exists on disk.
7. When the user chooses an entry, load the selected file and display its contents on a separate page.

## Deliverables
- Updated `web_app.py` with:
  - a main GET route for `/history` route that lists available file-backed exports
  - a route that loads and displays the selected file contents
  - JSON parsing logic for `data_exports.json`
- New or updated templates:
  - `templates/items.html` or similar for the item list
  - `templates/history.html` for selection of file-backed exports
  - `templates/history_detail.html` for displaying file contents

## Tasks
1. Add a `/history` route in `web_app.py` that filters `data_exports.json` entries to only those with existing `file_path` files.
2. Pass the parsed item collection to a Jinja2 template.
3. Build a template that loops through the item collection and renders HTML for each export record.
4. Create a template for `/history` that lets the user select an entry by filename.
5. Add a route to load the selected entry's file contents and render it on its own page.
6. Ensure missing files are excluded from history and do not appear for selection.
7. Update the README with instructions for `/history`.

## Files to create
- `web_app.py`
- `templates/items.html`
- `templates/history.html`
- `templates/history_detail.html`
- `data_exports.json` (if not already present)

---
# Chunk 7: Database Setup and Migration

## Goals
Migrate the application's data layer from JSON file storage to a SQLite database, while maintaining compatibility with Heroku hosting.

## Requirements
1. Choose SQLite as the recommended database for Heroku compatibility and ease of local development.
   - SQLite requires no server setup and ships with most Python installations.
   - Flask-SQLAlchemy simplifies ORM integration.
2. Define a SQL model representing a single export item (analogous to the current `data_exports.json` structure).
3. Configure Flask to connect to an SQLite database using Flask-SQLAlchemy.
4. Create database initialization logic to set up tables on first run.
5. Modify the `/items` and `/history` routes to query the database instead of reading `data_exports.json`.
6. Update the templates (`items.html` and `history.html`) to work with SQLite query results.
7. Provide a one-time migration script or function to transfer existing `data_exports.json` data into the database.

## Database Model: Export

Define an `Export` model with the following fields:

```
id (Integer, primary key)
filename (String, required) — the saved export filename
original_name (String) — original name before export
date (DateTime, required) — export timestamp
user_type (String) — role of the user (e.g., "Product Manager", "Developer")
repository (String) — repository URL or identifier
file_path (String) — local path to the saved file
action (String) — action type (e.g., "new_chat", "resume_saved_session")
created_at (DateTime) — database record creation timestamp
```

## Deliverables
- Updated `web_app.py` with:
  - Flask-SQLAlchemy initialization
  - `Export` model definition
  - Database setup logic
  - Modified routes to query the database
  - A migration function (or instructions) to import existing `data_exports.json` into the database
- Updated or new configuration file for database URL
- Updated `requirements.txt` to include Flask-SQLAlchemy
- Updated `templates/items.html` and `templates/history.html` to display database query results
- migration script or function to populate the database from JSON

## Tasks
1. Add Flask-SQLAlchemy to `requirements.txt`.
2. Configure Flask-SQLAlchemy in `web_app.py` with a SQLite database file path.
3. Define the `Export` model class using SQLAlchemy ORM decorators.
4. Add database initialization code to create tables if they do not exist.
5. Create a migration function that reads `data_exports.json` and inserts records into the `Export` table.
6. Modify the `/items` route to query all `Export` records from the database.
7. Modify the `/history` route to query only `Export` records with non-empty `file_path` values that exist on disk.
8. Update the `/history/view/<int:entry_index>` route to fetch the entry by database ID instead of list index.
9. Ensure the templates render database query results correctly (no JSON-specific logic).
10. Update the README with instructions for running the database setup and migration.

## Files to create or modify
- `web_app.py` (update with Flask-SQLAlchemy, models, and routes)
- `requirements.txt` (add Flask-SQLAlchemy)
- `templates/items.html` (update to work with ORM results)
- `templates/history.html` (update to work with ORM results)
- `templates/history_detail.html` (update to work with database ID)
- Optional: `migrate_json_to_db.py` (one-time migration script)
- `README.md` (update with database setup instructions)

---
# Chunk 8: Edit, Soft Delete, and AI Chat Continuation

## Goals

Allow users to update and soft delete saved export records from the web
interface. Extend the history detail page so users can continue a chat
with the AI and update the associated markdown file.

## Requirements

1.  Update `items.html` to include action links or buttons for each
    record:
    -   View
    -   Update
    -   Delete
2.  Add soft delete support to the database.
3.  Deleting a record should not remove it from the database.
4.  Deleted records should be hidden from normal item and history views.
5.  Clicking Delete must ask the user for confirmation before
    submitting.
6.  Clicking Update should load the existing history detail page for
    that export.
7.  The history detail page should include:
    -   the current markdown preview
    -   a chat-style text input
    -   a submit button to continue the conversation
8.  When the user submits new chat text:
    -   send the new text and current markdown content to the AI
        connection in `main.py`
    -   ask the AI to update the existing markdown content
    -   save the updated markdown back to the associated `.md` file
    -   reload the page and display the updated text in the preview

## Database Changes

Update the `Export` model to include soft delete fields:

``` python
deleted_at = db.Column(db.DateTime, nullable=True)
is_deleted = db.Column(db.Boolean, default=False)
```

Normal queries should filter out deleted records:

``` python
Export.query.filter_by(is_deleted=False).all()
```

## Deliverables

-   Updated `web_app.py` with:
    -   soft delete fields on the `Export` model
    -   filtered `/items` and `/history` routes
    -   delete route that marks records as deleted
    -   update route that loads the history detail page
    -   POST route for continuing the AI chat
-   Updated `templates/items.html` with:
    -   View link
    -   Update link
    -   Delete form or button
    -   JavaScript confirmation before delete
-   Updated `templates/history_detail.html` with:
    -   markdown preview area
    -   chat continuation form
    -   status message area after update
-   Updated database migration/setup logic for the new soft delete
    columns
-   Updated README instructions for editing and deleting saved exports

## Tasks

1.  Add `is_deleted` and `deleted_at` fields to the `Export` model.
2.  Update database initialization or migration logic to add the new
    fields.
3.  Modify `/items` so it only displays records where `is_deleted` is
    false.
4.  Modify `/history` so it only displays non-deleted records with valid
    `file_path` values.
5.  Update `templates/items.html` to display action links for each
    export record.
6.  Add a Delete button for each record.
7.  Add a JavaScript `confirm()` prompt before submitting the delete
    request.
8.  Create a POST route such as `/items/delete/<int:export_id>`.
9.  In the delete route:
    -   load the export by ID
    -   set `is_deleted` to true
    -   set `deleted_at` to the current timestamp
    -   save the record
    -   redirect back to `/items`
10. Add an Update link that routes to the existing history detail page,
    such as `/history/view/<int:export_id>`.
11. Update `history_detail.html` to include a chat input form below the
    markdown preview.
12. Create a POST route such as `/history/update/<int:export_id>`.
13. In the update route:

-   load the export by ID
-   read the associated markdown file
-   collect the user's new chat message from `request.form`
-   call the AI helper function in `main.py`
-   pass the current markdown and new user message to the AI
-   save the AI-updated markdown back to the same file path
-   redirect back to the detail page

14. Add error handling for:

-   missing export records
-   deleted records
-   missing markdown files
-   empty chat input
-   AI connection failures

15. Update the README with instructions for using Update and Delete.

## Files to create or modify

-   `web_app.py`
-   `main.py`
-   `templates/items.html`
-   `templates/history.html`
-   `templates/history_detail.html`
-   `README.md`
-   Optional: database migration script for adding soft delete columns


---
# Chunk 9: User Accounts, Authentication, and Data Ownership

## Goals

Add user accounts to the application so each saved export belongs to a
specific logged-in user. Protect all application routes behind login,
store passwords securely with salted hashes, and make sure users can
only view, update, or delete their own export records.

## Requirements

1.  Create a new `User` model in the database.
2.  The `User` model must include:
    -   `id`
    -   `username`
    -   `password_hash`
    -   `salt`
    -   `created_at`
3.  Passwords must never be stored as plain text.
4.  Passwords should be hashed using SHA with a unique salt per user.
5.  Modify the `Export` model to include a foreign key relationship to
    `User`.
6.  Each export record must belong to one user.
7.  Add registration functionality.
8.  Add login functionality using Flask sessions.
9.  Add logout functionality that clears the session.
10. All routes except login and registration must require a logged-in
    user.
11. Users must only be able to view, update, delete, or continue chats
    for exports they created.
12. Add encryption or security handling for user-owned data where
    appropriate.
13. Create a migration that inserts two demo users:

-   username: `demo-pm`
-   password: `demo`
-   username: `demo-dev`
-   password: `demo`

14. Create a migration that assigns all existing export records to the
    `demo-pm` user.

## Database Changes

Create a new `User` model:

``` python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

Update the `Export` model:

``` python
user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
user = db.relationship("User", backref="exports")
```

## Deliverables

-   Updated `web_app.py` with:
    -   `User` model
    -   updated `Export` model
    -   password hashing helper functions
    -   registration route
    -   login route
    -   logout route
    -   login-required route protection
    -   user ownership filtering on all export queries
-   New or updated templates:
    -   `templates/register.html`
    -   `templates/login.html`
    -   updated navigation with logout link
-   Database migration script with:
    -   new `users` table
    -   new `user_id` field on `exports`
    -   demo users
    -   assignment of existing exports to `demo-pm`
-   Updated README instructions for:
    -   registering
    -   logging in
    -   using demo accounts
    -   understanding route protection

## Tasks

1.  Add a `User` model to the database.
2.  Add a `user_id` foreign key field to the `Export` model.
3.  Add password helper functions to:
    -   generate a salt
    -   hash a password with SHA and salt
    -   verify a submitted password against the stored hash
4.  Create a `/register` route.
5.  Create a `register.html` template with:
    -   username field
    -   password field
    -   confirm password field
    -   submit button
6.  In the registration route:
    -   validate that the username is unique
    -   validate that passwords match
    -   generate a salt
    -   hash the password
    -   save the new user
    -   redirect to login
7.  Create a `/login` route.
8.  Create a `login.html` template with:
    -   username field
    -   password field
    -   submit button
9.  In the login route:
    -   find the user by username
    -   hash the submitted password using the stored salt
    -   compare the result to `password_hash`
    -   store `user_id` in the Flask session
    -   redirect to `/items`
10. Create a `/logout` route that clears the session and redirects to
    `/login`.
11. Add a `login_required` decorator.
12. Apply `login_required` to all routes except:

-   `/login`
-   `/register`
-   static files

13. Update `/items` so it only queries exports where:

-   `Export.user_id == session["user_id"]`
-   `Export.is_deleted == False`

14. Update `/history` so it only shows the logged-in user's non-deleted
    exports with valid files.
15. Update detail, update, and delete routes so users can only access
    records they own.
16. When creating a new export, automatically set `user_id` to the
    current logged-in user.
17. Add a migration to create the demo users:

-   `demo-pm / demo`
-   `demo-dev / demo`

18. Add a migration to assign all existing exports to the `demo-pm`
    user.
19. Add error handling for:

-   duplicate usernames
-   invalid login credentials
-   missing session
-   unauthorized export access
-   missing user records

20. Update the README with authentication and demo login instructions.

## Files to create or modify

-   `web_app.py`
-   `templates/register.html`
-   `templates/login.html`
-   `templates/items.html`
-   `templates/history.html`
-   `templates/history_detail.html`
-   `README.md`
-   Optional: `migrate_users.py`

## Security Notes

-   Do not store plain-text passwords.
-   Use a unique salt for each user.
-   Use Flask sessions to track logged-in users.
-   Set a strong Flask `SECRET_KEY`.
-   Filter every export query by the current user.
-   Never trust an export ID from the URL without checking ownership.
-   For stronger production security, use a password-specific hashing
    tool such as Werkzeug or bcrypt instead of plain SHA.

---
# Chunk 9.5: New Chat with AI-Generated Project Outline

## Goals
Allow users to start a new chat by providing a GitHub repository URL and project description, then use AI to generate a comprehensive project outline.

## Tasks - COMPLETED ✓
1. ✓ Create a page to start a new chat (`/new_chat`)
2. ✓ Ask user to link to a GitHub repo to use as a corpus of data
3. ✓ Allow user to paste project description into the chat
4. ✓ Use the AI connection in main.py to create an MD formatted file outlining the project
5. ✓ Create a new entry in the database and redirect to the history/view page for editing and copying

## Implementation Details

### New Route: `/new_chat`
- **GET**: Displays a form for creating a new chat
- **POST**: Processes the form and calls AI to generate project outline
- Protected by `@login_required` decorator

### New Template: `new_chat.html`
- User-friendly form with fields for:
  - GitHub repository URL
  - User type (Product Manager, Developer, QA Engineer)
  - Project description (textarea for detailed input)
- Clear instructions on how the process works
- Consistent styling with other templates

### Features
- AI integration using Groq API
- Automatic markdown file generation
- Database entry creation with file path tracking
- User ownership tracking
- Soft delete support (is_deleted flag)
- Redirect to history detail page for further editing
- Export directory creation (auto-mkdir)

### Database Changes
- Uses existing `Export` model
- Stores repository URL, user type, and action type for tracking

### Integration Points
- Links from `items.html` dashboard to new chat creation
- Uses existing AI client from `main.py` (get_groq_client)
- Integrates with history/detail view for subsequent editing
- Maintains user authentication and data ownership

## Files Created/Modified
- `templates/new_chat.html` - NEW: Form for starting new chat
- `web_app.py` - MODIFIED: Added `/new_chat` GET and POST routes
- `templates/items.html` - MODIFIED: Added "Start New Chat" button

## Testing Notes
- Flask app starts successfully
- Dependencies installed
- Syntax validation passed
- Routes are accessible and protected by login decorator 

--- 
# CHunk 10