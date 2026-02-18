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

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
   * May need to run pip3 or python3 -m pip instead

python3 -m pip install -r requirements.txt

3. **Set up your environment file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Get your free Groq API key from [https://console.groq.com](https://console.groq.com)
   - Open `.env` and replace `your_groq_api_key_here` with your actual API key:
     ```
     GROQ_API_KEY=gsk_your_actual_key_here
     ```
   - Set your save folder path (optional - will be prompted if not set):
     ```
     SAVE_FOLDER_PATH=~/Documents/JiraExports
     ```

## Running the Program

Run the main application:
```bash
python main.py
```

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

### Saved Chat Files

Chat exports are saved as markdown files (.md) that can be:
- Copied directly into Jira descriptions or comments
- Opened in any text editor or markdown viewer
- Used as reference for future tasks
- Continued later using the `OPEN` command

Files are saved with a timestamp to prevent overwriting and are tracked in `data_exports.json` for easy retrieval.

## Features (Current - Chunk 3)

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

## Project Structure

```
6200Project/
├── main.py              # Main application
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