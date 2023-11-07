from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'blogs'

mysql = MySQL(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = '123456'  # Secret key for JWT
jwt = JWTManager(app)

# User data (can be stored in a database)
# users = {
#     'user1': 'password1',
#     'user2': 'password2'
# }

# User Registration API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor()

    # Check if the username already exists in the database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return jsonify({"message": "Username already exists"}), 400

    # Create a new user and store it in the database
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "User registered successfully"}), 201

# User Login API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor()

    # Check the user's credentials in the database
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    cursor.close()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200

if __name__ == '__main__':
    app.run(debug=False)