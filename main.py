# imports from flask
import json
import os
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify  # import render_template from "public" flask libraries
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
from flask_login import current_user, login_required
from flask import current_app
from werkzeug.security import generate_password_hash
import shutil
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from api.leaderboard_api import add_leaderboard_entry, get_leaderboard  # Import the functions







# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects 
# API endpoints
from api.user import user_api 
from api.pfp import pfp_api
from api.nestImg import nestImg_api # Justin added this, custom format for his website
from api.post import post_api
from api.channel import channel_api
from api.group import group_api
from api.section import section_api
from api.nestPost import nestPost_api # Justin added this, custom format for his website
from api.messages_api import messages_api # Adi added this, messages for his website
from api.carphoto import car_api
from api.carChat import car_chat_api
from api.vote import vote_api
from api.guess import guess_api
from api.leaderboard_api import leaderboard_api
# database Initialization functions
from model.carChat import CarChat
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.nestPost import NestPost, initNestPosts # Justin added this, custom format for his website
from model.vote import Vote, initVotes
from model.guess import Guess
<<<<<<< HEAD
from model.leaderboard import  initLeaderboardTable  # Import the LeaderboardEntry model and init function
=======
from model.leaderboard import initLeaderboardTable
>>>>>>> 13090bc93c28e03270d80bc43ed0c751ec17455d
# server only Views

# register URIs for api endpoints
app.register_blueprint(messages_api) # Adi added this, messages for his website
app.register_blueprint(user_api)
app.register_blueprint(pfp_api) 
app.register_blueprint(post_api)
app.register_blueprint(channel_api)
app.register_blueprint(group_api)
app.register_blueprint(section_api)
app.register_blueprint(car_chat_api)
app.register_blueprint(guess_api)
app.register_blueprint(leaderboard_api)
# Added new files to create nestPosts, uses a different format than Mortensen and didn't want to touch his junk
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(car_api)

# Tell Flask-Login the view function name of your login route
login_manager.login_view = "login"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.path))

# register URIs for server pages
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Helper function to check if the URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', '') or request.form.get('next', '')
    if request.method == 'POST':
        user = User.query.filter_by(_uid=request.form['username']).first()
        if user and user.is_password(request.form['password']):
            login_user(user)
            if not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page or url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template("login.html", error=error, next=next_page)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/')  # connects default URL to index() function
def index():
    print("Home:", current_user)
    return render_template("index.html")

@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()
    return render_template("utable.html", user_data=users)

@app.route('/users/table2')
@login_required
def u2table():
    users = User.query.all()
    return render_template("u2table.html", user_data=users)

# Helper function to extract uploads for a user (ie PFP image)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
 
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Set the new password
    if user.update({"password": app.config['DEFAULT_PASSWORD']}):
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'error': 'Password reset failed'}), 500

# Create an AppGroup for custom commands
custom_cli = AppGroup('custom', help='Custom commands')

# Define a command to run the data generation functions
@custom_cli.command('generate_data')
def generate_data():
    initUsers()
    initSections()
    initGroups()
    initChannels()
    initPosts()
    initNestPosts()
    initVotes()
    
# Backup the old database
def backup_database(db_uri, backup_uri):
    """Backup the current database."""
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Backup not supported for production database.")

# Extract data from the existing database
def extract_data():
    data = {}
    with app.app_context():
        data['users'] = [user.read() for user in User.query.all()]
        data['sections'] = [section.read() for section in Section.query.all()]
        data['groups'] = [group.read() for group in Group.query.all()]
        data['channels'] = [channel.read() for channel in Channel.query.all()]
        data['posts'] = [post.read() for post in Post.query.all()]
    return data

# Save extracted data to JSON files
def save_data_to_json(data, directory='backup'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for table, records in data.items():
        with open(os.path.join(directory, f'{table}.json'), 'w') as f:
            json.dump(records, f)
    print(f"Data backed up to {directory} directory.")

# Load data from JSON files
def load_data_from_json(directory='backup'):
    data = {}
    for table in ['users', 'sections', 'groups', 'channels', 'posts']:
        with open(os.path.join(directory, f'{table}.json'), 'r') as f:
            data[table] = json.load(f)
    return data

# Restore data to the new database
def restore_data(data):
    with app.app_context():
        users = User.restore(data['users'])
        _ = Section.restore(data['sections'])
        _ = Group.restore(data['groups'], users)
        _ = Channel.restore(data['channels'])
        _ = Post.restore(data['posts'])
    print("Data restored to the new database.")

# Define a command to backup data
@custom_cli.command('backup_data')
def backup_data():
    data = extract_data()
    save_data_to_json(data)
    backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])

# Define a command to restore data
@custom_cli.command('restore_data')
def restore_data_command():
    data = load_data_from_json()
    restore_data(data)
    
# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)

# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}

def validate_request_data(data, required_keys):
    """
    Validate that the request data contains all required keys.
    :param data: The incoming JSON data
    :param required_keys: A set of keys that must be present in the data
    :return: (bool, str) indicating if validation passed and an error message if not
    """
    if not isinstance(data, dict):
        return False, "Request data must be a JSON object."
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    return True, ""

@app.route('/api/submit_guess', methods=['POST'])
def save_guess_simple():
    # Debugging: Log the incoming request
    print("Incoming request data:", request.json)

    try:
        # Parse JSON input
        data = request.json  # Expecting JSON input
        required_keys = {'user', 'guess', 'is_correct'}

        # Validate input data
        is_valid, error_message = validate_request_data(data, required_keys)
        if not is_valid:
            print("Validation failed:", error_message)  # Debugging
            return jsonify({"error": error_message}), 400

        # Extract values from the request
        user = data['user']
        guess = data['guess']
        is_correct = data['is_correct']

        # Initialize stats for the user if not present
        if user not in user_stats:
            user_stats[user] = {
                "correct": 0,
                "wrong": 0,
                "total_guesses": 0,
                "guesses": []
            }

        # Update user stats
        user_stats[user]["total_guesses"] += 1
        if is_correct:
            user_stats[user]["correct"] += 1
        else:
            user_stats[user]["wrong"] += 1

        # Append guess details to the user's history
        user_stats[user]["guesses"].append({
            "guess": guess,
            "is_correct": is_correct
        })

        # Append new guess to global chat logs
        chat_logs.append({
            "user": user,
            "guess": guess,
            "is_correct": is_correct
        })

        # Append new guess to the database
        new_guess = Guess(user,guess,is_correct
        )        
        new_guess.create()
       
        
        # Response format
        response_data = {
            "User": user,
            "Stats": {
                "Correct Guesses": user_stats[user]["correct"],
                "Wrong Guesses": user_stats[user]["wrong"],
                "Total Guesses": user_stats[user]["total_guesses"]
            },
            "Latest Guess": {
                "Guess": guess,
                "Is Correct": is_correct
            }
        }

        # Return success response with stats and latest guess
        return jsonify(response_data), 201

    except KeyError as e:
        print("KeyError:", str(e))  # Log and handle missing keys
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except TypeError as e:
        print("TypeError:", str(e))  # Log and handle type errors
        return jsonify({"error": f"Type error: {str(e)}"}), 400
    except Exception as e:
        # Log unexpected exceptions and provide better debugging info
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Initialize leaderboard_db
leaderboard_db = []  # Define the leaderboard_db here

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard_get():
    return get_leaderboard(leaderboard_db)  # Call the function to get leaderboard entries

@app.route('/api/leaderboard', methods=['POST'])
def leaderboard_post():
    return add_leaderboard_entry(leaderboard_db)  # Call the function to add a new entry

# this runs the flask application on the development server
if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port="8887")
