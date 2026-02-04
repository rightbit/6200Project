#!/usr/bin/env python3
"""
Better Jira Generator - CLI Prototype
A chatbot to help product managers and developers with Jira task descriptions.
"""

import os
import sys
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
from docx import Document


def check_env_file():
    """Check if .env file exists and has required API key."""
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


def chat_loop(client, role, repo_url, task_content=None, file_info=None):
    """Main chat loop with the LLM."""
    print("\n" + "="*60)
    print(f"          CHAT SESSION - {role.replace('_', ' ').upper()}")
    print("="*60)
    print("\nYou can now chat with the assistant.")
    print("Type 'EXIT' to quit or 'LIST' to view loaded resources.\n")
    
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
            print("-"*60)
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
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Get user role
        role = get_user_role()
        
        # Get task description file (optional)
        task_content, file_info = get_task_file()
        
        # Get GitHub repository
        repo_url = get_github_repo()
        
        # Start chat loop
        chat_loop(client, role, repo_url, task_content, file_info)
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please contact the program developer for assistance.")
        sys.exit(1)


if __name__ == "__main__":
    main()
