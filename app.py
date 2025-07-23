
from flask import Flask, render_template, request, redirect, url_for
from models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SECRET_KEY'] = 'Parking@123'


#connecting db and app with init_app
db.init_app(app)



def initialize_admin():
    admin = User.query.filter_by(username='Admin').first()
    if not admin:
        admin = User(username='Admin', 
                    email='admin@gmail.com', 
                    password='Admin123',
                    address='Admin_address',
                    pin_code='111111',
                    role='admin')
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        user_name = User.query.filter_by(username=username).first()
        ex_email = User.query.filter_by(email=email).first()
        if user_name or ex_email:
            return "User already exists"
        else:
            new_user = User(username=username, email=email, password=password, address=address, pin_code=pin_code)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = request.form.get('role')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/user_dashboard.html', methods=['GET', 'POST'])
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/admin.html', methods=['GET', 'POST'])
def admin():
    lots = Lot.query.all()
    users = User.query.filter(User.role == 'user').all()
    return render_template('admin.html', lots = lots, users=users)

@app.route('/new_parking.html', methods=['GET', 'POST'])
def new_parking():
    if request.method == 'POST':
        prime_location = request.form.get('prime_location')
        price = request.form.get('price')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        maximum_spots = int(request.form.get('maximum_spots'))
    
        new_lot = Lot(
            prime_location=prime_location,
            price=price,
            address=address,
            pin_code=pin_code,
            maximum_spots=maximum_spots
            )

        db.session.add(new_lot)
        db.session.commit()

        for i in range(1, maximum_spots + 1):
            spot = Spot(lot_id=new_lot.id, id=i)
            db.session.add(spot)

        return redirect(url_for('admin'))
    return render_template('new_parking.html')

@app.route('/edit_parking.html/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking(lot_id):
    lot = Lot.query.get_or_404(lot_id)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            return redirect(url_for('admin'))
        lot.prime_location = request.form.get('prime_location')
        lot.price = request.form.get('price')
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')
        lot.maximum_spots = request.form.get('maximum_spots')

        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit_parking.html', lot=lot)

@app.route('/test_add_user')
def test_add():
    user = User(username='test', email='t@t.com', password='123')
    db.session.add(user)
    db.session.commit()
    return "User added!"

@app.route('/lot/<int:lot_id>')
def view_spot(lot_id):
    lot = Lot.query.get_or_404(lot_id)

    # Fetch existing spots for this lot
    existing_spots = Spot.query.filter_by(lot_id=lot.id).order_by(Spot.spot_number).all()
    current_count = len(existing_spots)

    # Create missing spots (if any)
    if current_count < lot.maximum_spots:
        for i in range(current_count + 1, lot.maximum_spots + 1):
            new_spot = Spot(
                lot_id=lot.id,
                spot_number=i,
                status='available',
                user_id=1  # Or use a placeholder/default user or NULL if allowed
            )
            db.session.add(new_spot)
        db.session.commit()
        existing_spots = Spot.query.filter_by(lot_id=lot.id).order_by(Spot.spot_number).all()

    return render_template('view_spot.html', lot=lot, spots=existing_spots)

@app.route('/spot/<int:spot_id>')
def spot_details(spot_id):
    



if __name__ == '__main__':
    with app.app_context():         #initialisation of database
        db.create_all()
        initialize_admin()
    app.run(debug=True)