from flask import Flask, render_template, request, redirect, url_for
from models import *
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

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
        user_name = User.query.filter_by(username=username).first()
        ex_email = User.query.filter_by(email=email).first()
        if user_name or ex_email:
            return "User already exists"
        else:
            new_user = User(username=username, email=email, password=password)
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
                return redirect(url_for('user_dashboard', user_id=user.id))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/user_dashboard.html/<int:user_id>', methods=['GET', 'POST'])
def user_dashboard(user_id):
    booker = User.query.get(user_id)
    current_spot = Spot.query.filter_by(user_id=user_id, status="Booked").all()
    history = Release.query.filter_by(user_id=user_id).order_by(Release.released_at.desc()).all()
    return render_template('user_dashboard.html', booker=booker, current_spot=current_spot,history=history)

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
            spot = Spot(lot_id=new_lot.id, spot_number=i)
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


@app.route('/lot/<int:lot_id>/view')
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
                user_id=1 
            )
            db.session.add(new_spot)
        db.session.commit()
        existing_spots = Spot.query.filter_by(lot_id=lot.id).order_by(Spot.spot_number).all()

    return render_template('view_spot.html', lot=lot, spots=existing_spots)

@app.route('/book')
def book():
    user_id = request.args.get('user_id', type=int)
    lots = Lot.query.all()  
    booker = User.query.get_or_404(user_id)
    return render_template('lot.html', lots=lots, booker=booker)


@app.route('/book_spot/<int:lot_id>/<int:user_id>')
def book_spot(lot_id,user_id):
    lot = Lot.query.get_or_404(lot_id)
    spots = Spot.query.filter_by(lot_id=lot.id, status='available').order_by(Spot.spot_number).all()
    booker = User.query.get_or_404(user_id)
    return render_template('book_spot.html', lot=lot, spots=spots, booker=booker)


@app.route('/confirm_booking/<int:spot_id>/<int:user_id>')
def confirm_booking(spot_id,user_id):
    booker = User.query.get_or_404(user_id)
    spot = Spot.query.get_or_404(spot_id)
    spot.status="Booked"
    spot.user_id = user_id  
    db.session.commit()
    existing_release = Release.query.filter_by(spot_id=spot.id, user_id=user_id, released_at=None).first()
    if not existing_release:
        new_release = Release(
            spot_id=spot.id,
            user_id=user_id,
            parked_at=datetime.utcnow(),
            released_at=None,   # still parked
            cost=0              # will be calculated on release
        )
        db.session.add(new_release)
        db.session.commit()
    current_spot = Spot.query.filter_by(user_id=user_id, status="Booked").all()
    history = Release.query.filter_by(user_id=user_id).order_by(Release.released_at.desc()).all()
    return render_template('user_dashboard.html', booker=booker, current_spot=current_spot,history=history)

@app.route('/release/<int:spot_id>/<int:user_id>', methods=['POST'])
def release(spot_id,user_id):
    spot = Spot.query.get_or_404(spot_id)
    booker = User.query.get_or_404(user_id)
    last_release = Release.query.filter_by(spot_id=spot.id, user_id=user_id, released_at=None).first()
    parked_time = last_release.parked_at if last_release else datetime.utcnow()
    released_time = datetime.utcnow()
    duration_hours = max(1, int((released_time - parked_time).total_seconds() / 3600))
    cost = spot.lot.price*duration_hours
    return render_template('release.html',booker=booker, spot=spot, cost=cost)

@app.route('/confirm_release/<int:spot_id>/<int:user_id>', methods=['POST'])
def confirm_release(spot_id,user_id):
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            return redirect(url_for('user_dashboard', user_id=user_id))
        spot = Spot.query.get_or_404(spot_id)
        booker = User.query.get_or_404(user_id) 
        spot.status="available"
        spot.user_id = None
        db.session.commit()
        released_time = datetime.utcnow()
        
        # Find existing release with no released_at
        existing_release = Release.query.filter_by(spot_id=spot.id, user_id=booker.id, released_at=None).first()
        if existing_release:
            parked_time = existing_release.parked_at
            duration_hours = max(1, int((released_time - parked_time).total_seconds() / 3600))
            cost = spot.lot.price * duration_hours

            # Update it
            existing_release.released_at = released_time
            existing_release.cost = cost
            db.session.commit()

        current_spot = Spot.query.filter_by(user_id=user_id, status="Booked").all()
        history = Release.query.filter_by(user_id=user_id).order_by(Release.released_at.desc()).all()
        print("History count after release:", len(history)) 
    return render_template('user_dashboard.html', booker=booker,current_spot=current_spot,history=history)

@app.route('/search_lot')
def search_lot():
    search_word=request.args.get("search")
    key=request.args.get("key")
    if key == "prime_location":
        results=Lot.query.filter_by(prime_location=search_word).all()
    else:
        results=Lot.query.filter_by(pin_code=search_word).all()

    available_spots = {lot.id: Spot.query.filter_by(lot_id=lot.id, status='available').count()
    for lot in results}

    return render_template('lot_results.html', results=results,key=key, available_spots = available_spots)

@app.route('/search')
def search():
    search_word=request.args.get("search")
    key=request.args.get("key")
    if key == "prime_location":
        results=Lot.query.filter_by(prime_location=search_word).all()
    elif key == "username":
        results=User.query.filter_by(username=search_word).all()
    else:
        results=Lot.query.filter_by(pin_code=search_word).all()

    return render_template('results.html', results=results,key=key)

@app.route('/summary')
def admin_summary():
    lots = Lot.query.all()
    lot_names = []
    available_lots = []

    for lot in lots:
        lot_names.append(lot.prime_location)
        available = Spot.query.filter_by(lot_id=lot.id, status='available').count()
        available_lots.append(available)
    plt.figure(figsize=(10, 6))
    plt.bar(lot_names,available_lots)
    plt.xlabel('location of lot')
    plt.ylabel('availability')
    plt.title('Uses of lots')
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig('static/bar.png')
    plt.clf()

    return render_template('admin_summary.html', lot_names=lot_names, available_lots=available_lots)


@app.route("/user_summary/<int:user_id>")
def user_summary(user_id):
    booker = User.query.get_or_404(user_id)

    # Count bookings per lot by this user
    booking_data = (
        db.session.query(Lot.prime_location, db.func.count(Release.id))
        .join(Spot, Spot.lot_id == Lot.id)
        .join(Release, Release.spot_id == Spot.id)
        .filter(Release.user_id == user_id)
        .group_by(Lot.prime_location)
        .all()
    )

    lot_names = [row[0] for row in booking_data]
    booking_counts = [row[1] for row in booking_data]

    # Plotting
    plt.bar(lot_names, booking_counts)
    plt.xlabel("Lot")
    plt.ylabel("Bookings")
    plt.title(f"Your Booking Summary ({booker.username})")
    plt.xticks(rotation=45)
    plt.tight_layout()
  

    plt.savefig("static/user_summary.png")
    plt.clf()
    
    return render_template("user_summary.html", booker=booker, lot_names=lot_names, booking_counts=booking_counts)




if __name__ == '__main__':
    with app.app_context():         #initialisation of database
        db.create_all()
        initialize_admin()