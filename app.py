from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secretkey'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_address = db.Column(db.String(200), nullable=False)
    booking_date = db.Column(db.String(50), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    place = db.relationship('Place', backref=db.backref('bookings', lazy=True))

@app.route('/')
def index():
    places = Place.query.all()
    return render_template('index.html', places=places)

@app.route('/book/<int:place_id>', methods=['GET', 'POST'])
def book_place(place_id):
    place = Place.query.get_or_404(place_id)
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_address = request.form['user_address']
        booking_date = request.form['booking_date']
        new_booking = Booking(user_name=user_name, user_address=user_address, booking_date=booking_date, place_id=place.id)
        db.session.add(new_booking)
        db.session.commit()
        flash('Booking successful!')
        return redirect(url_for('index'))
    return render_template('book_place.html', place=place)

@app.route('/add_place', methods=['GET', 'POST'])
def add_place():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']
        amount = float(request.form['amount'])
        new_place = Place(name=name, description=description, image_url=image_url, amount=amount)
        db.session.add(new_place)
        db.session.commit()
        flash('Place added successfully!')
        return redirect(url_for('index'))
    return render_template('add_place.html')

@app.route('/admin/bookings', methods=['GET', 'POST'])
def admin_bookings():
    bookings = Booking.query.all()
    if request.method == 'POST':
        filter_name = request.form.get('filter_name', '').strip()
        if filter_name:
            bookings = Booking.query.filter(Booking.user_name.contains(filter_name)).all()
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/export_excel')
def export_excel():
    # Your logic to export data to an Excel file goes here
    return 'Excel file exported successfully!'

@app.route('/export_pdf')
def export_pdf():
    # Your logic to export data to a PDF file goes here
    return 'PDF file exported successfully!'

if __name__ == '__main__':
    app.run(debug=True)
