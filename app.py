"""
app.py

A Flask-based backend for a GPT-4 powered AI Agent.
It supports:
 - Conversation memory (stored in SQLite).
 - Voice/Text input from the front-end.
 - Toggleable voice or text output (handled by the browser).
 - Usage and estimated cost tracking for GPT-4.
"""

import os
import sqlite3
import openai
import traceback
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

# Name of the SQLite database file
DB_NAME = 'database.db'

# GPT-4 usage cost constants (as of time of writing):
#  $0.03 per 1K prompt tokens, $0.06 per 1K completion tokens.
GPT4_PROMPT_COST_PER_1K = 0.03
GPT4_COMPLETION_COST_PER_1K = 0.06

def init_db():
    """
    Initializes the database with tables for messages (conversation) and usage (token count).
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create usage table
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            cost REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on app startup
init_db()

def get_conversation_messages(limit=10):
    """
    Retrieve the most recent messages from the database.
    Return them as a list of dicts: [{'role': ..., 'content': ...}, ...]
    The `limit` determines how many messages from the tail of the conversation to retrieve.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()

    # Since we got them in reverse order, reverse them back
    rows.reverse()

    messages = []
    for row in rows:
        messages.append({'role': row[0], 'content': row[1]})
    return messages

def add_message_to_db(role, content):
    """
    Insert a new message into the messages table.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def record_usage(model, prompt_tokens, completion_tokens):
    """
    Record usage for each API call. 
    Also compute cost using GPT-4 pricing at the time of writing.
    """
    total_tokens = prompt_tokens + completion_tokens
    cost = (prompt_tokens / 1000.0 * GPT4_PROMPT_COST_PER_1K) + \
           (completion_tokens / 1000.0 * GPT4_COMPLETION_COST_PER_1K)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO usage (model, prompt_tokens, completion_tokens, total_tokens, cost) VALUES (?, ?, ?, ?, ?)',
              (model, prompt_tokens, completion_tokens, total_tokens, cost))
    conn.commit()
    conn.close()

def get_usage_summary():
    """
    Get the sum of tokens and cost to date.
    Returns a dict with total_prompt_tokens, total_completion_tokens, total_cost.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT SUM(prompt_tokens), SUM(completion_tokens), SUM(cost) FROM usage')
    row = c.fetchone()
    conn.close()

    total_prompt = row[0] if row[0] else 0
    total_completion = row[1] if row[1] else 0
    total_cost = row[2] if row[2] else 0
    return {
        'total_prompt_tokens': total_prompt,
        'total_completion_tokens': total_completion,
        'total_cost': round(total_cost, 5)  # round for readability
    }

def generate_chat_completion(messages):
    """
    Call the OpenAI ChatCompletion API with GPT-4 using the conversation messages.
    messages should be a list of dicts in the format: 
      [{'role': 'system'|'user'|'assistant', 'content': '...'}, ...]
    Return the assistant's reply as a string.
    Also record usage data in the usage table.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        # Extract the assistant's message
        assistant_message = response['choices'][0]['message']['content']

        # Record usage
        usage_info = response['usage']  # contains prompt_tokens, completion_tokens, total_tokens
        record_usage(
            model="gpt-4",
            prompt_tokens=usage_info['prompt_tokens'],
            completion_tokens=usage_info['completion_tokens']
        )

        return assistant_message

    except Exception as e:
        print("Error generating chat completion:", str(e))
        print(traceback.format_exc())
        return f"Error: {str(e)}"

@app.route('/')
def index():
    """
    Serve the main web page with the text/voice interface and theme toggle.
    """
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to handle chat messages from the front-end.
    Expects JSON with { user_input: string }.
    Returns JSON with { response: string }.
    """
    data = request.get_json()
    user_input = data.get('user_input', '')

    # Add the user message to the DB
    add_message_to_db('user', user_input)

    # Build up the conversation from the most recent 10 messages
    conversation_history = get_conversation_messages(limit=10)

    # Ask GPT-4
    assistant_reply = generate_chat_completion(conversation_history)

    # Store assistant's reply
    add_message_to_db('assistant', assistant_reply)

    return jsonify({'response': assistant_reply})

@app.route('/usage', methods=['GET'])
def usage():
    """
    Return total usage info in JSON format:
    {
      'total_prompt_tokens': ...
      'total_completion_tokens': ...
      'total_cost': ...
    }
    """
    summary = get_usage_summary()
    return jsonify(summary)

if __name__ == '__main__':
    # For production, consider setting debug=False and using a production server (e.g., gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)
