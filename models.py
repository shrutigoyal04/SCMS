# models.py
from flask_sqlalchemy import SQLAlchemy

# Create a db instance (initialized in app.py)
db = SQLAlchemy()

# ----------------- User Model -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.college_id}>'

# ----------------- Menu Item Model -----------------
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<MenuItem {self.name}>'

# ----------------- Order Model -----------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(20), db.ForeignKey('user.college_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Pending')

    def __repr__(self):
        return f'<Order {self.id} by {self.college_id}>'

# ----------------- Feedback Model -----------------
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(20), db.ForeignKey('user.college_id'), nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer)

    def __repr__(self):
        return f'<Feedback from {self.college_id}>'