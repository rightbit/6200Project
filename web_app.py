#!/usr/bin/env python3
"""
Better Jira Generator - Web Application
A web interface for the Better Jira Generator chatbot.
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    """Home route that displays a welcome message."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Better Jira Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-color: #f5f5f5;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello Web!</h1>
            <h3>This is Ryan Bouche's INFO-6200 assignment</h3>
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8080)
