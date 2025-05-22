

from flask import Flask, flash, redirect, render_template,request, jsonify, session, url_for
import json
import os
app = Flask(__name__,static_folder="static",static_url_path="/")
app.config["ENV"] = "production"

@app.route('/')
def index():
    json_path = os.path.join(app.root_path, 'data', 'skins.json')

    with open(json_path, 'r') as f:
        skins = json.load(f)
        last_three_skins = skins[-3:]

    return render_template('index.html',gd=last_three_skins)
@app.route('/test')
def test():
    json_path = os.path.join(app.root_path, 'data', 'skins.json')
    # Load the JSON file
    with open(json_path, 'r') as f:
        skins = json.load(f)


    return render_template('test.html',mylist=skins)
@app.route('/store')
def store():
    offset = int(request.args.get("offset", 0))
    json_path = os.path.join(app.root_path, 'data', 'skins.json')
    with open(json_path, 'r') as f:
        skins = json.load(f)

    batch = skins[offset:offset + 6]

    # If it's AJAX (for Load More), return JSON
    if request.args.get("ajax") == "1":
        return jsonify(batch)

    return render_template('acciunts.html', mylist=batch)


@app.route('/details/<int:id>')
def details(id):
    json_path = os.path.join(app.root_path, 'data', 'skins.json')
    # Load the JSON file
    with open(json_path, 'r') as f:
        skins = json.load(f)
    
    doskins = []

    for i in skins:
        if i["id"] == int(id):
            doskins = i
            return render_template('details.html',mylist=doskins)

            return "EROR"


@app.route('/contact')
def contact():
    return render_template('contact.html')


def get_cards_data():
    if 'cards' in session:
        return session['cards']
    else:
        json_path = os.path.join(app.root_path, 'data', 'skins.json')
        with open(json_path, 'r') as f:
            cards = json.load(f)
        session['cards'] = cards
        return cards

def save_cards_data(cards):
    session['cards'] = cards

@app.route('/get_cards')
def get_cards():
    cards = get_cards_data()
    return jsonify(cards)
@app.route('/update_cards', methods=['POST'])
def update_cards():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid data'}), 400

    # Save to session
    session['cards'] = data

    # Also update the skins.json file on disk
    json_path = os.path.join(app.root_path, 'data', 'skins.json')
    try:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return jsonify({'error': f'Failed to write to file: {str(e)}'}), 500

    return jsonify({'status': 'success'})

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'
app.secret_key = 'GEEHSGG11GErsd'  # Needed for flashing messages


@app.route('/admin', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin.html')

@app.route('/admin-dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('editcard.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))
