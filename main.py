#!/usr/bin/env python3
"""
Better Jira Generator - CLI Prototype
A chatbot to help product managers and developers with Jira task descriptions.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
from docx import Document


def check_env_file():
    """Check if .env file exists and has required API key and save folder."""
    if not Path('.env').exists():
        print("\n❌ ERROR: .env file not found!")
        print("Please create a .env file with your GROQ_API_KEY.")
        print("See .env.example for the required format.")
        print("\nContact the program developer if you need assistance.")
        sys.exit(1)
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_api_key_here':
        print("\n❌ ERROR: GROQ_API_KEY not configured!")
        print("Please add your Groq API key to the .env file.")
        print("Get your API key from: https://console.groq.com")
        print("\nContact the program developer if you need assistance.")
        sys.exit(1)
    
    return api_key


def check_save_folder():
    """Check if save folder is configured and exists, create if needed."""
    save_folder = os.getenv('SAVE_FOLDER_PATH')
    
    if not save_folder:
        print("\n⚠️  WARNING: SAVE_FOLDER_PATH not configured in .env file!")
        print("Please enter a folder path where chat exports will be saved.")
        print("Example: ~/Documents/JiraExports or /Users/username/JiraExports\n")
        
        while True:
            folder_input = input("Enter save folder path: ").strip()
            
            if folder_input.upper() == 'EXIT':
                print("\nGoodbye!")
                sys.exit(0)
            
            if folder_input:
                # Expand user home directory
                if folder_input.startswith('~'):
                    folder_input = os.path.expanduser(folder_input)
                
                save_folder = folder_input
                
                # Update .env file
                try:
                    with open('.env', 'r') as f:
                        env_content = f.read()
                    
                    if 'SAVE_FOLDER_PATH=' in env_content:
                        # Update existing line
                        lines = env_content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('SAVE_FOLDER_PATH='):
                                lines[i] = f'SAVE_FOLDER_PATH={save_folder}'
                        env_content = '\n'.join(lines)
                    else:
                        # Add new line
                        env_content += f'\nSAVE_FOLDER_PATH={save_folder}'
                    
                    with open('.env', 'w') as f:
                        f.write(env_content)
                    
                    print(f"✓ Save folder path added to .env")
                    break
                except Exception as e:
                    print(f"❌ Error updating .env file: {e}")
                    print("Please add SAVE_FOLDER_PATH to your .env file manually.")
                    sys.exit(1)
    
    # Expand user home directory if needed
    if save_folder.startswith('~'):
        save_folder = os.path.expanduser(save_folder)
    
    # Create folder if it doesn't exist
    save_path = Path(save_folder)
    if not save_path.exists():
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created save folder: {save_folder}")
        except Exception as e:
            print(f"❌ Error creating save folder: {e}")
            sys.exit(1)
    
    return str(save_path)


def load_exports_data():
    """Load the data_exports.json file."""
    exports_file = Path('data_exports.json')
    
    if not exports_file.exists():
        return {'exports': []}
    
    try:
        with open(exports_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Could not load exports data: {e}")
        return {'exports': []}


def save_exports_data(data):
    """Save data to data_exports.json file."""
    exports_file = Path('data_exports.json')
    try:
        with open(exports_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving exports data: {e}")


def load_session_data():
    """Load the saved_session.json file."""
    session_file = Path('saved_session.json')
    
    if not session_file.exists():
        return {}
    
    try:
        with open(session_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Could not load session data: {e}")
        return {}


def save_session_data(data):
    """Save data to saved_session.json file."""
    session_file = Path('saved_session.json')
    try:
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving session data: {e}")


def clear_session_data():
    """Clear the saved_session.json file."""
    session_file = Path('saved_session.json')
    try:
        with open(session_file, 'w') as f:
            json.dump({}, f, indent=2)
    except Exception as e:
        print(f"❌ Error clearing session data: {e}")


def check_saved_session():
    """Check if there's a saved session and ask if user wants to continue."""
    session_data = load_session_data()
    
    if not session_data or not session_data.get('role'):
        return None
    
    print("\n" + "="*60)
    print("          SAVED SESSION FOUND")
    print("="*60)
    print("\nYou have a saved session from your last use:")
    print(f"  Role: {session_data.get('role', 'N/A').replace('_', ' ').title()}")
    print(f"  Repository: {session_data.get('repository', 'N/A')}")
    
    if session_data.get('file_info'):
        print(f"  Task File: {session_data['file_info'].get('name', 'N/A')}")
    
    saved_date = session_data.get('timestamp')
    if saved_date:
        try:
            date_obj = datetime.fromisoformat(saved_date)
            print(f"  Last saved: {date_obj.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            pass
    
    print("\n" + "-"*60)
    
    while True:
        choice = input("\nWould you like to continue from this session? (y/n): ").strip().lower()
        
        if choice.upper() == 'EXIT':
            print("\nGoodbye!")
            sys.exit(0)
        
        if choice == 'y':
            return session_data
        elif choice == 'n':
            print("\n✓ Starting fresh session...")
            clear_session_data()
            return None
        else:
            print("❌ Please enter 'y' or 'n'.")


def save_chat_to_file(messages, save_folder, role, repo_url, file_info=None):
    """Save chat conversation to a markdown file."""
    print("\n" + "-"*60)
    print("SAVE CHAT")
    print("-"*60)
    
    # Prompt for filename
    while True:
        filename = input("\nEnter filename (without extension): ").strip()
        
        if filename.upper() == 'EXIT':
            return None
        
        if not filename:
            print("❌ Filename cannot be empty.")
            continue
        
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_')
        
        if not filename:
            print("❌ Please enter a valid filename.")
            continue
        
        break
    
    # Create full file path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.md"
    file_path = Path(save_folder) / full_filename
    
    # Build markdown content
    content = f"""# Better Jira Generator - Chat Export

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Role:** {role.replace('_', ' ').title()}  
**Repository:** {repo_url}  
"""
    
    if file_info:
        content += f"**Task File:** {file_info['name']}  \n"
    
    content += "\n---\n\n"
    
    # Add conversation (skip system message)
    for msg in messages[1:]:  # Skip system prompt
        if msg['role'] == 'user':
            content += f"## User\n\n{msg['content']}\n\n"
        elif msg['role'] == 'assistant':
            content += f"## Assistant\n\n{msg['content']}\n\n"
    
    # Save file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Register in data_exports.json
        exports_data = load_exports_data()
        export_entry = {
            'filename': full_filename,
            'original_name': filename,
            'date': datetime.now().isoformat(),
            'user_type': role.replace('_', ' ').title(),
            'repository': repo_url,
            'file_path': str(file_path)
        }
        exports_data['exports'].append(export_entry)
        save_exports_data(exports_data)
        
        print(f"\n✓ Chat saved successfully!")
        print(f"  File: {full_filename}")
        print(f"  Location: {file_path}")
        
        return full_filename
        
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")
        return None


def list_chat_history():
    """Display list of saved chats."""
    exports_data = load_exports_data()
    exports = exports_data.get('exports', [])
    
    if not exports:
        print("\n" + "-"*60)
        print("No saved chats found.")
        print("-"*60)
        return
    
    print("\n" + "="*60)
    print("CHAT HISTORY")
    print("="*60)
    
    for i, export in enumerate(exports, 1):
        date_obj = datetime.fromisoformat(export['date'])
        date_str = date_obj.strftime("%Y-%m-%d %H:%M")
        
        print(f"\n{i}. {export['original_name']}")
        print(f"   File: {export['filename']}")
        print(f"   Date: {date_str}")
        print(f"   Role: {export['user_type']}")
        print(f"   Repo: {export['repository']}")
    
    print("\n" + "="*60)


def load_chat_from_file(save_folder):
    """Load an existing chat file and return its messages."""
    exports_data = load_exports_data()
    exports = exports_data.get('exports', [])
    
    if not exports:
        print("\n❌ No saved chats found.")
        return None, None, None
    
    # Display list
    list_chat_history()
    
    print("\nEnter the number of the chat to open (or 'cancel' to go back):")
    
    while True:
        choice = input("\nChoice: ").strip()
        
        if choice.upper() in ['EXIT', 'CANCEL']:
            return None, None, None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(exports):
                export = exports[idx]
                file_path = Path(export['file_path'])
                
                if not file_path.exists():
                    print(f"\n❌ File not found: {file_path}")
                    print("The file may have been moved or deleted.")
                    print("\nWhat would you like to do?")
                    print("1. Delete this entry from history")
                    print("2. Keep the entry in history")
                    
                    while True:
                        action = input("\nChoice (1 or 2): ").strip()
                        
                        if action == '1':
                            # Remove entry from exports
                            exports.remove(export)
                            exports_data['exports'] = exports
                            save_exports_data(exports_data)
                            print("\n✓ Entry removed from history.")
                            break
                        elif action == '2':
                            print("\n✓ Entry kept in history.")
                            break
                        else:
                            print("❌ Please enter 1 or 2.")
                    
                    continue
                
                # Read the file and extract messages
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse markdown content back to messages
                messages = []
                sections = content.split('## ')
                
                for section in sections[1:]:  # Skip header
                    if section.startswith('User'):
                        msg_content = section.replace('User\n\n', '', 1).strip()
                        messages.append({'role': 'user', 'content': msg_content})
                    elif section.startswith('Assistant'):
                        msg_content = section.replace('Assistant\n\n', '', 1).strip()
                        messages.append({'role': 'assistant', 'content': msg_content})
                
                print(f"\n✓ Loaded chat: {export['original_name']}")
                print(f"  {len(messages)} messages loaded")
                
                return messages, export.get('repository', ''), export.get('user_type', '').lower().replace(' ', '_')
            else:
                print(f"❌ Please enter a number between 1 and {len(exports)}.")
        except ValueError:
            print("❌ Please enter a valid number.")


def get_user_role():
    """Prompt user to select their role."""
    print("\n" + "="*60)
    print("          BETTER JIRA GENERATOR - CLI PROTOTYPE")
    print("="*60)
    print("\nWelcome! Please select your role:\n")
    print("1. Product Manager - Focus on feature requirements")
    print("2. Developer - Focus on implementation and file structure")
    print("\nType 'EXIT' at any time to quit the program.\n")
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice.upper() == 'EXIT':
            print("\nGoodbye!")
            sys.exit(0)
        
        if choice == '1':
            return 'product_manager'
        elif choice == '2':
            return 'developer'
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


def read_file_content(file_path):
    """Read content from PDF, TXT, or DOCX file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None, "File not found"
    
    try:
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), None
        
        elif extension == '.pdf':
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return '\n'.join(text), None
        
        elif extension in ['.doc', '.docx']:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text), None
        
        else:
            return None, f"Unsupported file type: {extension}"
    
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def get_task_file():
    """Ask user if they want to provide a task description file."""
    print("\n" + "-"*60)
    print("Do you have a task description file? (PDF, TXT, DOC/DOCX)")
    print("This can be a requirements document, spec, or any task details.")
    print("-"*60 + "\n")
    
    while True:
        choice = input("Provide a file? (y/n): ").strip().lower()
        
        if choice.upper() == 'EXIT':
            print("\nGoodbye!")
            sys.exit(0)
        
        if choice == 'y':
            while True:
                file_path = input("\nEnter file path (or 'skip' to continue without): ").strip()
                
                if file_path.upper() == 'EXIT':
                    print("\nGoodbye!")
                    sys.exit(0)
                
                if file_path.lower() == 'skip':
                    return None, None
                
                # Handle paths with or without quotes
                file_path = file_path.strip('"\'')
                
                # Expand user home directory
                if file_path.startswith('~'):
                    file_path = os.path.expanduser(file_path)
                
                content, error = read_file_content(file_path)
                
                if error:
                    print(f"❌ {error}")
                    print("Please try again or type 'skip' to continue without a file.")
                else:
                    file_info = {
                        'path': file_path,
                        'name': Path(file_path).name,
                        'size': len(content),
                        'type': Path(file_path).suffix.lower()
                    }
                    print(f"✓ File loaded successfully: {file_info['name']}")
                    print(f"  ({file_info['size']} characters read)")
                    return content, file_info
        
        elif choice == 'n':
            return None, None
        else:
            print("❌ Please enter 'y' or 'n'.")


def get_github_repo():
    """Get GitHub repository URL from user."""
    print("\n" + "-"*60)
    print("Please provide a GitHub repository URL to use as context.")
    print("(For this prototype, we'll note the repo for future implementation)")
    print("-"*60 + "\n")
    
    while True:
        repo = input("GitHub repository URL: ").strip()
        
        if repo.upper() == 'EXIT':
            print("\nGoodbye!")
            sys.exit(0)
        
        if repo:
            print(f"✓ Repository noted: {repo}")
            print("(Full repo analysis will be implemented in future versions)")
            return repo
        else:
            print("❌ Please enter a valid repository URL.")


def get_system_prompt(role, repo_url, task_content=None):
    """Generate system prompt based on user role and optional task file."""
    task_context = ""
    if task_content:
        task_context = f"\n\nThe user has provided this task description:\n---\n{task_content}\n---\n"
    
    if role == 'product_manager':
        return f"""You are an AI assistant helping a Product Manager write clear, detailed Jira task descriptions.
        
The codebase you're working with is at: {repo_url}{task_context}

Your goals:
- Help create specific, actionable task descriptions
- Ask clarifying questions about feature requirements
- Suggest acceptance criteria
- Consider edge cases and user experience
- Focus on WHAT needs to be built, not HOW to build it

Be concise, professional, and focus on gathering clear requirements."""
    
    else:  # developer
        return f"""You are an AI assistant helping a Developer implement Jira tasks.

The codebase you're working with is at: {repo_url}{task_context}

Your goals:
- Help identify which files need to be modified
- Suggest implementation approaches
- Explain code structure and architecture patterns
- Point out relevant functions, classes, or modules
- Focus on HOW to implement features

Be technical, specific, and focus on code implementation details."""


def show_help():
    """Display help information with available commands."""
    print("\n" + "="*60)
    print("          AVAILABLE COMMANDS")
    print("="*60)
    print("\n  NEW     - Start a new chat session")
    print("  SAVE    - Save current chat to markdown file")
    print("  HISTORY - View saved chat history")
    print("  OPEN    - Open and continue a saved chat")
    print("  LIST    - View loaded resources")
    print("  HELP    - Show this help message")
    print("  EXIT    - Quit the program")
    print("\n" + "="*60)


def chat_loop(client, role, repo_url, task_content=None, file_info=None, save_folder=None):
    """Main chat loop with the LLM."""
    print("\n" + "="*60)
    print(f"          CHAT SESSION - {role.replace('_', ' ').upper()}")
    print("="*60)
    print("\nYou can now chat with the assistant.")
    print("\nType 'HELP' to see available commands.\n")
    
    # Initialize conversation history
    system_prompt = get_system_prompt(role, repo_url, task_content)
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        if user_input.upper() == 'EXIT':
            print("\n" + "="*60)
            print("Thank you for using Better Jira Generator!")
            print("="*60 + "\n")
            break
        
        # Handle NEW command
        if user_input.upper() == 'NEW':
            print("\n" + "-"*60)
            print("Starting new chat session...")
            print("-"*60)
            messages = [{"role": "system", "content": system_prompt}]
            clear_session_data()
            print("✓ New chat session started.")
            continue
        
        # Handle SAVE command
        if user_input.upper() == 'SAVE':
            if len(messages) <= 1:
                print("\n❌ No conversation to save yet.")
                continue
            
            saved_file = save_chat_to_file(messages, save_folder, role, repo_url, file_info)
            if saved_file:
                print("\nYou can continue chatting or type EXIT to quit.")
            continue
        
        # Handle HISTORY command
        if user_input.upper() == 'HISTORY':
            list_chat_history()
            continue
        
        # Handle OPEN command
        if user_input.upper() == 'OPEN':
            loaded_messages, loaded_repo, loaded_role = load_chat_from_file(save_folder)
            
            if loaded_messages:
                # Update current conversation
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(loaded_messages)
                
                print("\n✓ Chat loaded. You can continue the conversation.")
            continue
        
        # Handle LIST command
        if user_input.upper() == 'LIST':
            print("\n" + "-"*60)
            print("LOADED RESOURCES")
            print("-"*60)
            print(f"Role: {role.replace('_', ' ').title()}")
            print(f"Repository: {repo_url}")
            if file_info:
                print(f"\nTask File:")
                print(f"  Name: {file_info['name']}")
                print(f"  Path: {file_info['path']}")
                print(f"  Type: {file_info['type']}")
                print(f"  Size: {file_info['size']:,} characters")
            else:
                print("\nTask File: None")
            print(f"\nSave Folder: {save_folder}")
            print(f"Messages in current chat: {len(messages) - 1}")  # Exclude system message
            print("-"*60)
            continue
        
        # Handle HELP command
        if user_input.upper() == 'HELP':
            show_help()
            continue
        
        if not user_input:
            continue
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Call Groq API
            print("\nAssistant: ", end="", flush=True)
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            
            assistant_message = response.choices[0].message.content
            print(assistant_message)
            
            # Add assistant response to history
            messages.append({"role": "assistant", "content": assistant_message})
            
        except Exception as e:
            print(f"\n❌ Error communicating with Groq API: {e}")
            print("Please check your API key and internet connection.")


def main():
    """Main application entry point."""
    try:
        # Check environment setup
        api_key = check_env_file()
        
        # Check and setup save folder
        save_folder = check_save_folder()
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Check for saved session
        saved_session = check_saved_session()
        
        if saved_session:
            # Resume from saved session
            role = saved_session.get('role')
            repo_url = saved_session.get('repository')
            file_info = saved_session.get('file_info')
            
            # Load task content if file exists
            task_content = None
            if file_info and file_info.get('path'):
                content, error = read_file_content(file_info['path'])
                if not error:
                    task_content = content
                    print(f"✓ Task file reloaded: {file_info['name']}")
                else:
                    print(f"⚠️  Could not reload task file: {error}")
                    file_info = None
        else:
            # Get user role
            role = get_user_role()
            
            # Get task description file (optional)
            task_content, file_info = get_task_file()
            
            # Get GitHub repository
            repo_url = get_github_repo()
            
            # Save initial session data
            session_data = {
                'role': role,
                'repository': repo_url,
                'file_info': file_info,
                'timestamp': datetime.now().isoformat()
            }
            save_session_data(session_data)
        
        # Start chat loop
        chat_loop(client, role, repo_url, task_content, file_info, save_folder)
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please contact the program developer for assistance.")
        sys.exit(1)


if __name__ == "__main__":
    main()
