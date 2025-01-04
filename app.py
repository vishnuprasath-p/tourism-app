from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import tempfile

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
    bookings = Booking.query.all()
    data = {
        'ID': [booking.id for booking in bookings],
        'User Name': [booking.user_name for booking in bookings],
        'User Address': [booking.user_address for booking in bookings],
        'Booking Date': [booking.booking_date for booking in bookings],
        'Place ID': [booking.place_id for booking in bookings]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Bookings')
    writer.close()
    output.seek(0)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        tmp_file.write(output.read())
        tmp_file_path = tmp_file.name

    return send_file(tmp_file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='bookings.xlsx')

@app.route('/export_pdf')
def export_pdf():
    bookings = Booking.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Booking List", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(20, 10, txt="ID", border=1)
    pdf.cell(40, 10, txt="User Name", border=1)
    pdf.cell(50, 10, txt="User Address", border=1)
    pdf.cell(40, 10, txt="Booking Date", border=1)
    pdf.cell(20, 10, txt="Place ID", border=1)
    pdf.ln()

    for booking in bookings:
        pdf.cell(20, 10, txt=str(booking.id), border=1)
        pdf.cell(40, 10, txt=booking.user_name, border=1)
        pdf.cell(50, 10, txt=booking.user_address, border=1)
        pdf.cell(40, 10, txt=booking.booking_date, border=1)
        pdf.cell(20, 10, txt=str(booking.place_id), border=1)
        pdf.ln()

    # Use pdf.output directly with BytesIO and provide name argument
    output = BytesIO()
    pdf.output(dest='S').encode('latin1')
    output.write(pdf.output(dest='S').encode('latin1'))
    output.seek(0)

    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='bookings.pdf')





if __name__ == '__main__':
    app.run(debug=True)
