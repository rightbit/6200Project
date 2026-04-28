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
