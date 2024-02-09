from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from datetime import date
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
admin = Admin(app, name='User Admin', template_mode='bootstrap3')

# Define User and Reservation models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    unit_number = db.Column(db.String(20), nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_amount = db.Column(db.Numeric(8, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    selected_date = db.Column(db.Date, nullable=False)
    selected_time = db.Column(db.String(50), nullable=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    announcement_title = db.Column(db.String(200), nullable=False)
    announcement_date = db.Column(db.Date, nullable=False)
    announcement_detail = db.Column(db.String(1000), nullable=False)

# Create a subclass of the ModelView class for the User model (admin)
class UserView(ModelView):
    column_list = ('name', 'email', 'password', 'unit_number')
    column_searchable_list = ('name', 'email')
    column_editable_list = ('password', 'unit_number')
    form_columns = ('name', 'email', 'password', 'unit_number')

# Add the view to the admin instance (admin)
admin.add_view(UserView(User, db.session, name='Users'))

# Create a subclass of the ModelView class for the Payment model (admin)
class PaymentView(ModelView):
    column_list = ('name', 'payment_method', 'payment_amount', 'payment_date')
    column_searchable_list = ('name',)
    column_filters = ('payment_method', 'payment_date')
    form_columns = ('name', 'payment_method', 'payment_amount', 'payment_date')

# Add the Payment view to the admin instance
admin.add_view(PaymentView(Payment, db.session, name='Payments'))

# Create a subclass of the ModelView class for the Reservation model (admin)
class ReservationView(ModelView):
    column_list = ('username', 'location', 'selected_date', 'selected_time')
    column_searchable_list = ('username', 'location')
    column_filters = ('selected_date', 'selected_time')
    form_columns = ('username', 'location', 'selected_date', 'selected_time')

# Add the Reservation view to the admin instance
admin.add_view(ReservationView(Reservation, db.session, name='Reservations'))

# Create a subclass of the ModelView class for the Announcement model (admin)
class AnnouncementView(ModelView):
    column_list = ('announcement_title', 'announcement_date', 'announcement_detail')
    column_searchable_list = ('announcement_title', 'announcement_detail')
    column_filters = ('announcement_date',)
    form_columns = ('announcement_title', 'announcement_date', 'announcement_detail')

# Add the Announcement view to the admin instance
admin.add_view(AnnouncementView(Announcement, db.session, name='Announcements'))

# Create all tables within app context
with app.app_context():
    db.create_all()


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

        # Check if any user with the provided data already exists
        existing_user = User.query.filter(
            (User.name == name) | (User.email == email) | (User.unit_number == unit_number)
        ).first()

        if existing_user:
            return render_template('signup.html', message='User with the provided information already exists. Please use different information.')

        # Create a new user if the provided data doesn't exist
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

@app.route('/selection')
def selection():
    return render_template('Selection.html')

@app.route('/payment')
def paymentoption():
    return render_template('PaymentOption.html')

@app.route('/process_selection', methods=['POST'])
def process_selection():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Safely get the 'activity' value from the form data
    location = request.form.get('activity')
    # Check if the activity was provided
    if not location:
        # If not, flash a message and redirect back to the selection page
        # Make sure to import Flask's flash function: from flask import flash
        flash("Please select an activity.", "error")
        return redirect(url_for('selection'))

    selected_date = request.form.get('selected_date')
    selected_time = request.form.get('selected_time')
    
    # Ensure all fields are filled, otherwise, redirect back
    if not all([selected_date, selected_time]):
        flash("All fields are required.", "error")
        return redirect(url_for('selection'))

    # Convert the date string to a date object
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format.", "error")
        return redirect(url_for('selection'))

    username = session['username']
    
    # Create a new reservation
    reservation = Reservation(username=username, location=location, selected_date=selected_date, selected_time=selected_time)

    # Add the reservation to the database
    db.session.add(reservation)
    db.session.commit()

    # Redirect to slot_summary page with reservation details
    return redirect(url_for('slot_summary'))


# Modify the slot_summary route to handle the latest or a specific reservation
@app.route('/slot_summary')
def slot_summary():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    reservation = Reservation.query.filter_by(username=username).order_by(Reservation.id.desc()).first()

    if reservation:
        return render_template('slot_summary.html', username=username, reservation=reservation)
    else:
        return "No reservation found for this user."

@app.route('/ewalletoption')
def ewalletoption():
    return render_template('EWalletOption.html')

@app.route('/onlinebanking')
def onlinebanking():
    return render_template('OnlineBanking.html')

@app.route('/submit', methods=['POST'])
def submit():
    card_number = request.form['card_number'].replace(" ", "")
    cvc = request.form['cvc']
    expiration_month = request.form['expiration_month']
    expiration_year = request.form['expiration_year']

    errors = []

    if len(card_number) != 16 or not card_number.isdigit():
        errors.append("Please enter a valid 16-digit card number.")

    if len(cvc) != 3 or not cvc.isdigit():
        errors.append("Please enter a valid 3-digit CVC.")

    current_year = int(str(date.today().year)[-2:])
    if len(expiration_year) != 2 or int(expiration_year) <= current_year:
        errors.append("Please enter a valid expiration year (YY) that is greater than the current year.")

    if len(expiration_month) != 2 or not expiration_month.isdigit() or not (1 <= int(expiration_month) <= 12):
        errors.append("Please enter a valid 2-digit month (MM) between 01 and 12.")
 
    if errors:
        return render_template('OnlineBanking.html', errors=errors)
    else:
        return render_template(('PaymentSuccessful.html'))
    
@app.route('/success')
def success():
    return render_template('PaymentSuccessful.html')

@app.route('/outstandingfees')
def outstandingfees():
    return render_template('OutstandingFees.html')

@app.route('/announcements')
def announcements():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch announcements from the database (this is a placeholder, you'll need to implement the actual retrieval logic)
    announcements = [
        {'title': 'Gym Update', 'content': 'The gym will be closed tomorrow.', 'author': 'Admin'},
        {'title': 'Pool Party', 'content': 'Join us for a pool party this Saturday!', 'author': 'Admin'}
        
    ]

    return render_template('announcements.html', announcements=announcements)

if __name__ == '__main__':
    app.run(debug=True)
