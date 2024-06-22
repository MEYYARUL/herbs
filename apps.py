from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to establish database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='herbs',
        user='root',
        password='root'
    )
    return connection

# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

# Route to handle user logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Route to display home page with products
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

# Route to add a new product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert new product into the database
            cursor.execute('INSERT INTO products (name, description, price) VALUES (%s, %s, %s)',
                           (name, description, price))
            connection.commit()
            connection.close()

            return redirect(url_for('add_product'))

        except mysql.connector.Error as e:
            print(f"Error inserting product: {e}")
            return 'Error inserting product'

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)
