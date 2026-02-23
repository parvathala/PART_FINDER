import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps

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
    return render_template('index.html', user_email=session.get('user_email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == REVIEW_USER["email"] and password == REVIEW_USER["password"]:
            session['logged_in'] = True
            session['user_email'] = email
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_email', None)
    return redirect(url_for('login'))

@app.route('/api/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])

    if df_parts.empty:
        return jsonify({"error": "Data not loaded on server."}), 500

    # Search Logic A & B: Check if query exactly matches any of the 4 columns
    # Pandas filtering logic:
    mask = (
        (df_parts['product_id_pcs'].str.upper() == query) |
        (df_parts['product_id_triad'].str.upper() == query) |
        (df_parts['distributor_part_number'].str.upper() == query) |
        (df_parts['alternate_part_number'].str.upper() == query)
    )
    
    results_df = df_parts[mask]
    
    # Convert to list of dicts, drop duplicates just in case
    results_dict = results_df.drop_duplicates().to_dict('records')
    
    return jsonify(results_dict)

# Call load_data immediately so it executes when gunicorn imports the app
load_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
