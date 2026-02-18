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

