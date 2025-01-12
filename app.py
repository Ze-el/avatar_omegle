from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import requests
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit, join_room, leave_room

# Load environment variables from .env file (replace 'path/to/.env' with your actual path)
load_dotenv()
app = Flask(__name__, static_folder='static')
app.config.from_object('config.Config')

# Set up a secret key for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY')

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        ssl_ca=os.getenv('CA_CERT_PATH'),
        ssl_disabled=False
    )
    return connection

def create_database_and_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DATABASE']}")
    cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            interests TEXT
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/')
def index():
    return render_template('index.html')


def get_user_info(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user




@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to edit your profile!')
        return redirect(url_for('index'))
    user_id = session['user_id']  # Get the logged-in user's ID
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Fetch user details by ID
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('logout'))
    # Handle profile update and action
    if request.method == 'POST':
        action = request.form.get('action')  # Get the action (Save Changes or Suggest More Interests)
        if action == "Save Changes":
            # Save the updated profile
            username = request.form['username']
            email = request.form['email']
            interests = request.form['interests']
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
            cursor.execute("""
                UPDATE users
                SET username = %s, email = %s, interests = %s
                WHERE id = %s
            """, (username, email, interests, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Profile updated successfully!')
            return redirect(url_for('profile'))
        elif action == "Suggest More Interests":
            # Get interests from form and make API request
            interests = request.form['interests']
            suggestions = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"Based on the user's interests: {interests}\nRewrite in a list separated form a more grammatically correct form of the list as well as additional interests based on their current ones."}
                        ]
                    }
                ],
                "systemInstruction": {
                    "role": "system",
                    "parts": [
                        {"text": "Rewrite in list form a list of interests. Just output a comma-separated list."}
                    ]
                }
            }
            api_key = os.getenv('API_KEY')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=suggestions)
                response.raise_for_status()  # Raise an exception for HTTP error responses
                response_content = response.json()['candidates'][0]['content']['parts'][0]['text']
                
                # Update user interests in the database
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
                cursor.execute("""
                    UPDATE users
                    SET interests = %s
                    WHERE id = %s
                """, (response_content, user_id))
                connection.commit()
                cursor.close()
                connection.close()
                flash('Interests updated based on suggestions!')
                return redirect(url_for('profile'))
            except requests.exceptions.RequestException as e:
                flash(f"Error fetching suggestions: {e}")
                return redirect(url_for('profile'))
    # Pass the correct user data to the template
    return render_template('profile.html', user=user)





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['user_id'] = user['id']
  # Set user_id in the session
            flash('Logged in successfully!')
            return render_template('profile.html', user=user)
        else:
            flash('Invalid username or password. Please try again.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print ("u")
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
        cursor.execute("SELECT * FROM users WHERE email = %s AND username= %s", (email,username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email or username already exists! Please try logging in.')
            return redirect(url_for('login'))
        

    
        


        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, password))
        connection.commit()
        print("User inserted successfully\n", flush=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        print ("Hey", flush=True)
        print (user, flush=True)
        connection.commit()
        cursor.close()
        connection.close()
        if user:
            session['user_id'] = user['id']
            print ("success", flush=True)
  # Set user_id in the session
            flash('Logged in successfully!')
            return render_template('profile.html', user=user)
        else:
            print ("No", flush=True)
            flash('Invalid username or password. Please try again.')
        print ("helooooo", flush=True)
        return redirect(url_for('signup'))

    return render_template('signup.html')




active_rooms = {}
user_matches = {}



@app.route('/match')
def match():
    if 'user_id' not in session:
        flash('You must be logged in to view matches!')
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Fetch the logged-in user's interests
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")
    cursor.execute("SELECT interests FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('logout'))

    user_interests = user['interests']
    
    api_key = os.getenv('API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    # Find matches based on refined interests
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"USE {app.config['MYSQL_DATABASE']}")

    try:
        cursor.execute("SELECT * FROM users WHERE id != %s", (user_id,))
        potential_matches = cursor.fetchall()
    except Exception as e:
        cursor.close()
        connection.close()
        flash(f"Error fetching matches: {e}")
        return redirect(url_for('index'))

    if not potential_matches:
        cursor.close()
        connection.close()
        flash("No matches found.")
        return render_template('matches.html', match=None)

    for potential_match in potential_matches:
        match_suggestions = {
            "contents": [
                {
                    "parts": [
                        {"text": f"User A's interests: {user_interests}\nUser B's interests: {potential_match['interests']}\nDetermine if User A and User B should match based on interests."}
                    ]
                }
            ],
            "systemInstruction": {
                "role": "system",
                "parts": [
                    {"text": "Analyze whether these two sets of interests are compatible and return Yes or No. Just return Yes or No."}
                ]
            }
        }

        try:
            match_response = requests.post(url, headers={'Content-Type': 'application/json'}, json=match_suggestions)
            match_result = match_response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if match_result == "Yes":
                # Create a unique room ID using user IDs
                room_id = f"room_{min(user_id, potential_match['id'])}_{max(user_id, potential_match['id'])}"

                
                # Store room information
                active_rooms[room_id] = {
                    'user1': min(user_id, potential_match['id']),
                    'user2': max(user_id, potential_match['id'])
                }
                
                # Store match information
                user_matches[user_id] = {
                    'match': potential_match,
                    'room_id': room_id
                }
                
                # Emit socket event for match found
                
                
                cursor.close()
                connection.close()
                
                return render_template('matches.html', 
                                     match=potential_match,
                                     room_id=room_id)
                
        except Exception as e:
            print(f"Error processing match: {e}")
            continue

    cursor.close()
    connection.close()
    flash("No matches found based on your interests.")
    return render_template('matches.html', match=None)







if __name__ == '__main__':
    # Check if running in development environment
    create_database_and_tables()
    app.run(host='0.0.0.0', port=5501)
   