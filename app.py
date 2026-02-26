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

# --- Couchbase Connection setup ---
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterTimeoutOptions, QueryOptions
from datetime import timedelta

cb_cluster = None
cb_bucket_name = os.getenv("COUCHBASE_BUCKET_NAME", "qgic-gg")

def init_couchbase():
    global cb_cluster
    host = os.getenv("COUCHBASE_HOST", "couchbase://10.201.68.111")
    username = os.getenv("COUCHBASE_USERNAME", "webdev")
    password = os.getenv("COUCHBASE_PASSWORD", "webdev123")
    connect_timeout = int(os.getenv("COUCHBASE_CONNECT_TIMEOUT", "30"))
    query_timeout = int(os.getenv("COUCHBASE_QUERY_TIMEOUT", "10"))
    kv_timeout = int(os.getenv("COUCHBASE_KV_TIMEOUT", "2"))

    auth = PasswordAuthenticator(username, password)
    timeout_options = ClusterTimeoutOptions(
        connect_timeout=timedelta(seconds=connect_timeout),
        query_timeout=timedelta(seconds=query_timeout),
        kv_timeout=timedelta(seconds=kv_timeout)
    )
    options = ClusterOptions(authenticator=auth, timeout_options=timeout_options)

    print(f"Connecting to Couchbase at {host}...")
    try:
        cb_cluster = Cluster(host, options)
        cb_cluster.wait_until_ready(timedelta(seconds=10))
        print("Connected successfully to Couchbase!")
    except Exception as e:
        print(f"Failed to connect to Couchbase: {e}")
        # Not exiting immediately so the app can still try to serve or reconnect later
        cb_cluster = None

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
            {"role": "system", "content": "You are a helpful IT/Sales assistant. Extract the exact part numbers from the user's message, search the database using the tool, and accurately present the results to the user. ALWAYS present the search results strictly in a structured Markdown table format with columns for Product ID (PCS), Product ID (Triad), Distributor Part Num, and Alternate Part Number. Do not use bullet points."}
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

    if not cb_cluster:
        return jsonify({"error": "Database connection not available."}), 500

    n1ql_query = f"""
        SELECT
            content.legacyNumber as product_id_triad,
            content.itemDesc,
            content.itemKey as product_id_pcs,
            content.distributorPartNumber as distributor_part_number,
            content.manufacturerPartNumber as alternate_part_number
        FROM `{cb_bucket_name}`
        WHERE divisionKey = "1"
          AND class = "com.pcs.api.productmaintenance.productcatalog.entity.Product"
          AND (content.legacyNumber LIKE $search_term
               OR TO_STRING(content.itemKey) LIKE $search_term
               OR content.distributorPartNumber LIKE $search_term
               OR content.manufacturerPartNumber LIKE $search_term)
        LIMIT 100
    """
    try:
        # Use prefix matching (trailing wildcard only) for performance with B-tree indexes
        search_param = f"{query}%"
        
        query_result = cb_cluster.query(
            n1ql_query,
            QueryOptions(named_parameters={'search_term': search_param})
        )
        
        results_dict = [row for row in query_result.rows()]
        
        # Deduplicate
        unique_results = []
        seen = set()
        for row in results_dict:
            t = tuple(sorted(row.items()))
            if t not in seen:
                seen.add(t)
                unique_results.append(row)
                
        return jsonify(unique_results)
    except Exception as e:
        import traceback
        import sys
        traceback.print_exc(file=sys.stdout)
        print(f"Couchbase Search Error: {e}", flush=True)
        return jsonify({"error": f"Failed to execute database search. {str(e)}"}), 500


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
        {"role": "system", "content": "You are a helpful IT/Sales assistant. Extract the exact part numbers from the user's message, search the database using the tool, and accurately present the results to the user. ALWAYS present the search results strictly in a structured Markdown table format with columns for Product ID (PCS), Product ID (Triad), Distributor Part Num, and Alternate Part Number. Do not use bullet points."}
    ])
    
    messages.append({"role": "user", "content": user_message})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_parts",
                "description": "Searches the parts database for a given product_id_pcs, product_id_triad, distributor_part_number, or alternate_part_number to find compatibilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The item key, part number, or keyword to search for",
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
                    
                    if not cb_cluster:
                        function_response = json.dumps({"error": "Database connection not available."})
                    else:
                        n1ql_query = f"""
                            SELECT
                                content.legacyNumber as product_id_triad,
                                content.itemDesc,
                                content.itemKey as product_id_pcs,
                                content.distributorPartNumber as distributor_part_number,
                                content.manufacturerPartNumber as alternate_part_number
                            FROM `{cb_bucket_name}`
                            WHERE divisionKey = "1"
                              AND class = "com.pcs.api.productmaintenance.productcatalog.entity.Product"
                              AND (content.legacyNumber LIKE $search_term
                                   OR TO_STRING(content.itemKey) LIKE $search_term
                                   OR content.distributorPartNumber LIKE $search_term
                                   OR content.manufacturerPartNumber LIKE $search_term)
                            LIMIT 100
                        """
                        try:
                            # Use prefix matching (trailing wildcard only) for performance with B-tree indexes
                            search_param = f"{query}%"
                            
                            query_result = cb_cluster.query(
                                n1ql_query,
                                QueryOptions(named_parameters={'search_term': search_param})
                            )
                            results_dict = [row for row in query_result.rows()]
                            
                            # Deduplicate
                            unique_results = []
                            seen = set()
                            for row in results_dict:
                                t = tuple(sorted(row.items()))
                                if t not in seen:
                                    seen.add(t)
                                    unique_results.append(row)
                                    
                            function_response = json.dumps(unique_results)
                        except Exception as e:
                            print(f"Couchbase Tool Search Error: {e}")
                            function_response = json.dumps({"error": "Failed to execute database search."})
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

# Initialize Couchbase connection immediately so it executes when app starts
init_couchbase()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
