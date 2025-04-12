# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from models import db, User, MenuItem, Order, Feedback
from werkzeug.security import generate_password_hash

# Load environment variables from .env
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Configuration
    app.config.from_object('config.Config')
    app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

    # Initialize the database
    db.init_app(app)

    # ----------------------- Routes -----------------------

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            college_id = request.form['college_id']
            password = request.form['password']
            user = User.query.filter_by(college_id=college_id).first()
            if user and password == user.password:
                session['user'] = user.college_id
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials.', 'danger')
                return redirect(url_for('login'))
        return render_template('login.html')
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already exists")
                return redirect(url_for('signup'))

            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful. Please login.")
            return redirect(url_for('login'))

        return render_template('signup.html')

    @app.route('/order', methods=['GET', 'POST'])
    def order():
        items = MenuItem.query.all()
        return render_template('order.html', items=items)

    @app.route('/add_to_cart/<int:item_id>', methods=['POST'])
    def add_to_cart(item_id):
        quantity = int(request.form.get('quantity', 1))

        if not item_id:
            flash("No item selected.", "warning")
            return redirect(url_for('order'))

        # Initialize cart if not present
        if 'cart' not in session:
            session['cart'] = []

        # Add item to cart
        cart = session['cart']
        cart.append({'item_id': item_id, 'quantity': quantity})
        session['cart'] = cart
        flash("Item added to cart!", "info")
        return redirect(url_for('order'))

    @app.route('/cart', methods=['GET', 'POST'])
    def cart():
        if request.method == 'POST' and 'item_id' in request.form:
            # Add item to cart
            item_id = request.form.get('item_id')
            quantity = int(request.form.get('quantity', 1))

            if not item_id:
                flash("No item selected.", "warning")
                return redirect(url_for('order'))

            if 'cart' not in session:
                session['cart'] = []

            cart = session['cart']
            cart.append({'item_id': item_id, 'quantity': quantity})
            session['cart'] = cart
            flash("Item added to cart!", "info")
            return redirect(url_for('order'))

        # Else handle order placement (Place Order button)
        cart_items = []
        if 'cart' in session:
            for entry in session['cart']:
                item = MenuItem.query.get(int(entry['item_id']))
                if item:
                    cart_items.append({
                        'item': item,
                        'quantity': entry['quantity'],
                        'total_price': item.price * int(entry['quantity'])
                    })

        # Place the order from cart
        if request.method == 'POST' and not 'item_id' in request.form:
            college_id = session.get('user')
            if not college_id:
                flash("Please log in to place order.", "warning")
                return redirect(url_for('login'))

            for entry in session['cart']:
                new_order = Order(college_id=college_id, item_id=entry['item_id'], quantity=entry['quantity'])
                db.session.add(new_order)

            db.session.commit()
            session.pop('cart', None)
            flash("Order placed successfully from cart!", "success")
            return redirect(url_for('dashboard'))

        return render_template('cart.html', cart_items=cart_items)

    @app.route('/feedback', methods=['GET', 'POST'])
    def feedback():
        if request.method == 'POST':
            college_id = session.get('user')
            message = request.form['message']
            rating = request.form.get('rating', 5)
            if college_id:
                new_feedback = Feedback(college_id=college_id, comment=message, rating=rating)
                db.session.add(new_feedback)
                db.session.commit()
                flash('Thanks for your feedback!', 'info')
            return redirect(url_for('feedback'))
        return render_template('feedback.html')

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        flash('Logged out successfully.', 'info')
        return redirect(url_for('home'))

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/menu')
    def menu():
        items = MenuItem.query.all()
        return render_template('menu.html', items=items)

    # ------------------------------------------------------

    with app.app_context():
        db.create_all()

    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
