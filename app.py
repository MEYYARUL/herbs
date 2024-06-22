from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='herbs'
    )
    return connection

# Route for home page
@app.route('/')
def index():
    return redirect(url_for('login'))

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']
        pincode = request.form['pincode']
        phone_number = request.form['phone_number']
        username = request.form['username']
        password = request.form['password']

        # Hash password before storing in database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Database connection and insertion
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (name, email, country, state, city, address, pincode, phone_number, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                       (name, email, country, state, city, address, pincode, phone_number, username, hashed_password))
        connection.commit()
        connection.close()

        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        connection.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

# Route for home page after login
@app.route('/home')
def home():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    connection.close()

    return render_template('home.html', products=products)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/product/<int:product_id>')
def view_product(product_id):
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    connection.close()

    if product is None:
        return 'Product not found', 404

    return render_template('view_product.html', product=product)

@app.route('/confirm_order/<int:product_id>', methods=['POST'])
def confirm_order(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    order_date = datetime.now()

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO orders (user_id, product_id, order_date) VALUES (%s, %s, %s)', 
                   (user_id, product_id, order_date))
    connection.commit()
    connection.close()
    # Logic to handle order confirmation, e.g., saving order to the database
    # For now, just redirect to the home page or display a confirmation message
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
def order_confirmation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT name FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    connection.close()

    return render_template('order_confirmation.html', user=user)



if __name__ == '__main__':
    app.run(debug=True)
