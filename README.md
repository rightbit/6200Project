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

## Running the Program

Run the main application:
```bash
python main.py
```

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
   - **Use `LIST` to view loaded resources** (role, repository, uploaded files)
   - Type `EXIT` at any time to quit

### Commands During Chat

- **`LIST`** - Display all loaded resources:
  - Your current role
  - GitHub repository URL
  - Task file details (name, path, type, size)
- **`EXIT`** - Quit the program

## Features (CLI Prototype - Chunk 1)

✅ Role-based chat interface (Product Manager or Developer)  
✅ Integration with Groq LLM (using Llama 3.1)  
✅ File upload support (PDF, TXT, DOC/DOCX) for task descriptions  
✅ `LIST` command to view loaded resources  
✅ Conversation history maintained throughout session  
✅ Error handling for missing environment configuration  
✅ Clean exit with EXIT command  

## Project Structure

```
6200Project/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your API keys (not committed to git)
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