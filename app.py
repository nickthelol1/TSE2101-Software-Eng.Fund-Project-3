from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_url_path='/static')  # Add this line to configure static files
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# ... (rest of your code)z

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            message = 'Incorrect username or password'

    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', message='Username already exists. Please choose another username.')

        # Create a new user if the username doesn't exist
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        username = session['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        user = User.query.filter_by(username=username, password=old_password).first()
        if user:
            if old_password == new_password:
                message = 'New password must be different from the old password.'
            else:
                user.password = new_password
                db.session.commit()
                message = 'Password changed successfully!'
        else:
            message = 'Incorrect old password'

    return render_template('change_password.html', message=message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
