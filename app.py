import os
import pandas as pd
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from openai import OpenAI
import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-for-testing'

# --- Hardcoded User for Review ---
REVIEW_USER = {
    "email": "test@test.com",
    "password": "password"
}

# --- Load CSV Data into Memory ---
CSV_FILE = 'PARTS_DATA.csv'
df_parts = pd.DataFrame()

def load_data():
    global df_parts
    if os.path.exists(CSV_FILE):
        print(f"Loading {CSV_FILE} into memory...")
        df_parts = pd.read_csv(CSV_FILE, dtype=str).fillna("")
        df_parts.rename(columns={
            'PRODUCT_ID_PCS': 'product_id_pcs',
            'PRODUCT_ID_TRIAD': 'product_id_triad',
            'DISTRIBUTOR_PART_NUMBER': 'distributor_part_number',
            'ALTERNATE_PART_NUMBER': 'alternate_part_number'
        }, inplace=True)
        print(f"Loaded {len(df_parts)} rows.")
    else:
        print(f"WARNING: {CSV_FILE} not found. Search will not return results.")

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
@login_required
def index():
    if 'chat_history' not in session:
        session['chat_history'] = [
            {"role": "system", "content": "You are a helpful IT/Sales assistant. Extract the exact part numbers from the user's message, search the database using the tool, and accurately present the results to the user. ALWAYS present the search results strictly in a structured Markdown table format with columns for Product ID (PCS), Product ID (TRIAD), Distributor Part Num, and Alternate Part Num. Do not use bullet points."}
        ]
    return render_template('index.html', user_email=session.get('user_email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == REVIEW_USER["email"] and password == REVIEW_USER["password"]:
            session['logged_in'] = True
            session['user_email'] = email
            session.pop('chat_history', None)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])

    if df_parts.empty:
        return jsonify({"error": "Data not loaded on server."}), 500

    mask = (
        (df_parts['product_id_pcs'].str.upper() == query) |
        (df_parts['product_id_triad'].str.upper() == query) |
        (df_parts['distributor_part_number'].str.upper() == query) |
        (df_parts['alternate_part_number'].str.upper() == query)
    )
    
    results_df = df_parts[mask]
    results_dict = results_df.drop_duplicates().to_dict('records')
    
    return jsonify(results_dict)


@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return jsonify({"reply": "OpenAI API Key is not configured. Please set the OPENAI_API_KEY environment variable and restart the server."})
        
    client = OpenAI(api_key=api_key)
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"reply": "I didn't catch that. Could you repeat it?"})

    messages = session.get('chat_history', [
        {"role": "system", "content": "You are a helpful IT/Sales assistant. Extract the exact part numbers from the user's message, search the database using the tool, and accurately present the results to the user. ALWAYS present the search results strictly in a structured Markdown table format with columns for Product ID (PCS), Product ID (TRIAD), Distributor Part Num, and Alternate Part Num. Do not use bullet points."}
    ])
    
    messages.append({"role": "user", "content": user_message})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_parts",
                "description": "Searches the parts database for a given product ID or part number to find compatibilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The Product ID or Part Number to search for (e.g., 'TDI1000106', '56003342')",
                        }
                    },
                    "required": ["query"],
                },
            }
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            # Append the tool call message itself to history
            messages.append(response_message.to_dict())
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_parts":
                    query = function_args.get("query", "").strip().upper()
                    
                    if df_parts.empty:
                        function_response = json.dumps({"error": "Data catalog empty."})
                    else:
                        mask = (
                            (df_parts['product_id_pcs'].str.upper() == query) |
                            (df_parts['product_id_triad'].str.upper() == query) |
                            (df_parts['distributor_part_number'].str.upper() == query) |
                            (df_parts['alternate_part_number'].str.upper() == query)
                        )
                        results_df = df_parts[mask]
                        function_response = json.dumps(results_df.drop_duplicates().to_dict('records'))
                        
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
            
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            final_reply = second_response.choices[0].message.content
            messages.append({"role": "assistant", "content": final_reply})
            
            final_reply_html = markdown.markdown(final_reply, extensions=['tables'])
            
            session['chat_history'] = messages
            session.modified = True
            
            return jsonify({"reply": final_reply_html})
            
        else:
            messages.append({"role": "assistant", "content": response_message.content})
            session['chat_history'] = messages
            session.modified = True
            
            final_reply_html = markdown.markdown(response_message.content, extensions=['tables'])
            return jsonify({"reply": final_reply_html})

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return jsonify({"reply": "I'm sorry, I encountered an error communicating with the AI service."})

# Call load_data immediately so it executes when gunicorn imports the app
load_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
