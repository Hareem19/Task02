from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify

from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'blogs'

mysql = MySQL(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a secret key for JWT
jwt = JWTManager(app)

# User Registration API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type')
    cursor = mysql.connection.cursor()

    # Check if the username or email already exists in the database
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return jsonify({"message": "Username or email already exists"}), 400

    # Create a new user and store it in the database
    cursor.execute("INSERT INTO users (username, email, password,user_type) VALUES (%s, %s, %s,%s)", (username, email, password,user_type))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "User registered successfully"}), 201



# User Login API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
 
    cursor = mysql.connection.cursor()

    # Check the user's credentials in the database
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate a JWT token for the user
    access_token = create_access_token(identity=user[0])
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

# Create a New Blog Post API
@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_blog_post():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    user_id = get_jwt_identity()

    if not title or not content:
        return jsonify({"message": "Title and content are required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)", (title, content, user_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Blog post created successfully"}), 201

# Post Comments API
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def post_comment(post_id):
    data = request.json
    comment_text = data.get('comment_text')
    user_id = get_jwt_identity()

    if not comment_text:
        return jsonify({"message": "Comment text is required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)", (post_id, user_id, comment_text))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Comment posted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=False)