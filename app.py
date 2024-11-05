from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered')
            return redirect(url_for('signup'))

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can log in now.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('profile'))

        flash('Invalid email or password')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)

@app.route('/products')
def products():
    products_list = [
        {'name': 'Product 1', 'description': 'Description for product 1', 'price': 10.99},
        {'name': 'Product 2', 'description': 'Description for product 2', 'price': 15.49},
        {'name': 'Product 3', 'description': 'Description for product 3', 'price': 7.99},
    ]
    return render_template('products.html', products=products_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    if request.method == 'POST':
        # Retrieve ingredients and prices from the form
        ingredients = request.form.getlist('ingredient')
        prices = request.form.getlist('price')
        
        total_cost = sum(float(price) for price in prices)
        
        # Example of recipe suggestions based on the total cost
        recipes = suggest_recipes(total_cost)
        
        return render_template('recipes.html', total_cost=total_cost, recipes=recipes)
    
    return render_template('calculator.html')

def suggest_recipes(total_cost):
    # This is a mock function; replace with actual logic for recipe suggestions
    if total_cost < 10:
        return ["Simple Salad", "Egg Fried Rice"]
    elif total_cost < 20:
        return ["Pasta Primavera", "Chicken Stir Fry"]
    else:
        return ["Steak Dinner", "Lamb Curry"]

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
