import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import joblib

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-please-change')
mongo = PyMongo(app)

model = joblib.load('student_model.pkl')


# Ensure a master/admin user exists if ADMIN_USERNAME and ADMIN_PASSWORD are provided
def create_admin_user():
    admin_user = os.getenv('ADMIN_USERNAME')
    admin_pw = os.getenv('ADMIN_PASSWORD')
    admin_email = os.getenv('ADMIN_EMAIL', '')
    if admin_user and admin_pw:
        existing = mongo.db.users.find_one({'username': admin_user})
        if not existing:
            pw_hash = generate_password_hash(admin_pw)
            mongo.db.users.insert_one({'username': admin_user, 'password': pw_hash, 'email': admin_email, 'role': 'admin'})


create_admin_user()


@app.route('/health')
def health():
    return 'ok', 200

@app.route('/')
def index():
    # Require login to access prediction form
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))

    study = float(request.form['study_hours'])
    attr = float(request.form['attendance'])
    prev = float(request.form['prev_score'])
    
    # Normalize study hours (0-12 to 0-1 range) for the model
    study_normalized = study / 12
    
    prediction = model.predict([[study_normalized, attr, prev]])[0]
    final_score = round(min(100, max(0, prediction)), 2)
    
    mongo.db.predictions.insert_one({
        "study_hours": study,
        "attendance": attr,
        "previous_score": prev,
        "predicted_score": final_score,
        "user": session.get('username')
    })
    return render_template('result.html', score=final_score)

@app.route('/dashboard')
def dashboard():
    # only show logged-in user's predictions
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))

    username = session['username']
    history = list(mongo.db.predictions.find({"user": username}).sort("_id", -1))

    # Simple lists for the chart (user-specific)
    labels = [f"Entry {i+1}" for i in range(len(history))][::-1]
    scores = [record['predicted_score'] for record in history][::-1]

    return render_template('dashboard.html', history=history, labels=labels, scores=scores)

@app.route('/delete/<id>')
def delete_record(id):
    # Allow deletion only for the owner or admin
    rec = mongo.db.predictions.find_one({'_id': ObjectId(id)})
    if not rec:
        flash('Record not found', 'warning')
        return redirect(url_for('dashboard'))

    username = session.get('username')
    is_admin = session.get('is_admin', False)
    if rec.get('user') and username and (rec.get('user') == username or is_admin):
        mongo.db.predictions.delete_one({'_id': ObjectId(id)})
        flash('Record deleted', 'success')
    else:
        flash('Not authorized to delete this record', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/history')
def history():
    # show history: users see only their history; admin sees everyone
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))

    username = session['username']
    if session.get('is_admin', False):
        history = list(mongo.db.predictions.find().sort('_id', -1))
    else:
        history = list(mongo.db.predictions.find({"user": username}).sort('_id', -1))

    # aggregate labels and scores for the chart
    labels = [f"Entry {i+1}" for i in range(len(history))][::-1]
    scores = [record['predicted_score'] for record in history][::-1]

    return render_template('history.html', history=history, labels=labels, scores=scores)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check users collection first
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user.get('password', ''), password):
            session['username'] = username
            # set admin flag when appropriate
            session['is_admin'] = (user.get('role') == 'admin')
            flash('Logged in successfully', 'success')
            next_page = request.args.get('next') or url_for('dashboard')
            return redirect(next_page)

        # Fallback to environment admin (legacy/demo)
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        if username == admin_username and password == os.getenv('ADMIN_PASSWORD', 'Vishnu@250906'):
            session['username'] = username
            session['is_admin'] = True
            flash('Logged in (admin) successfully', 'success')
            next_page = request.args.get('next') or url_for('dashboard')
            return redirect(next_page)

        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out', 'info')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        if not username or not password:
            flash('Please provide both username and password', 'warning')
            return redirect(url_for('signup'))

        # Check uniqueness
        if mongo.db.users.find_one({'username': username}):
            flash('Username already taken', 'warning')
            return redirect(url_for('signup'))

        pw_hash = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': pw_hash, 'email': email, 'role': 'user'})
        session['username'] = username
        session['is_admin'] = False
        flash('Account created and logged in', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))

    username = session['username']
    user = mongo.db.users.find_one({'username': username})
    preds_count = mongo.db.predictions.count_documents({'user': username})
    return render_template('profile.html', user=user, preds_count=preds_count)


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    # delete user's predictions and user document
    # some older records may have used different field names; remove any matching entries
    mongo.db.predictions.delete_many({'$or': [{'user': username}, {'username': username}]})
    mongo.db.users.delete_one({'username': username})
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Your account and all your predictions have been deleted', 'info')
    return redirect(url_for('signup'))
if __name__ == '__main__':
    app.run(debug=True)