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
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    unit_number = db.Column(db.String(20), nullable=False)


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
        name = request.form['name']
        password = request.form['password']

        # Check if the user with the given name and password exists
        user = User.query.filter_by(name=name, password=password).first()

        if user:
            session['username'] = name
            return redirect(url_for('index'))
        else:
            message = 'Incorrect name or password'

    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        unit_number = request.form['unit_number']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', message='Email already exists. Please use another email address.')

        # Create a new user if the email doesn't exist
        new_user = User(name=name, email=email, password=password, unit_number=unit_number)
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

        # Retrieve the user from the database
        user = User.query.filter_by(name=username, password=old_password).first()

        if user:
            # Update the password
            user.password = new_password

            # Commit changes to the database
            db.session.commit()
            message = 'Password changed successfully!'
        else:
            message = 'Failed to change password, please try again.'

    return render_template('change_password.html', message=message)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
