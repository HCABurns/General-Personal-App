# Web imports
from flask import Flask, jsonify, request, render_template, flash

# Firebase imports
from firebase_admin import credentials, db, initialize_app, auth

# Extra imports
import os
import json

# Create flask app.
app = Flask(__name__)
app.config['MAX_CONTENT_PATH'] = 16 * 1000000  # 16MB limit
app.secret_key = os.environ["SECRET_KEY"]

def get_data(ref):
    """
    Function to retrieve information from the database and return it.

    args:
        ref (str): String of the name of the table in the database to retrieve data from.

    Returns:
        list: Return a list of dicts of requested data.
    """
    info = db.reference(ref).get()
    if type(info) == dict:
        return info
    info_with_ids = []
    for id, data in enumerate(info):
        info_with_id = data
        info_with_id["id"] = id
        info_with_ids.append(data)
    return info_with_ids


def initialize_firebase():
    """
    Function to initialise the connection to the database and retrieve the required information.

    Due to these being mostly static data, only retrieve the data once and store.

    Returns:
        races or []: Returns list of dicts where each item is a race.
        games or []: Returns list of dicts where each item is a football game.
        epic_games or []: Returns list of dicts where each item is a free epic game.

    Raises:
        Exception e: If the connection to the database fails.
        KeyError: Fails to find the DB_URL.
    """
    try:
        # Load Firebase JSON from Render secret file
        firebase_json_path = "/etc/secrets/firebase.json"
        with open(firebase_json_path, "r") as f:
            firebase_config = json.load(f)

        cred = credentials.Certificate(firebase_config)
        initialize_app(cred, {'databaseURL': os.environ["DB_URL"]})

        print("Firebase initialized. Successfully retrieved data.")
        # Get the information from the database and return
        return True
    except Exception as e:
        print(f"Error occurred during Firebase initialization: {e}")
        return False


def verify_firebase_token():
    """
    Verify the Firebase ID token from the request header.

    Checks that the request includes a valid Firebase ID token in the Authorization
    header in the format: "Bearer <token>". Decodes and verifies the token.

    Returns:
        tuple:
            str or None: The UID of the authenticated user, or None if verification fails.
            Response or None: A Flask JSON response with error details if verification fails, else None.
            int or None: HTTP status code if verification fails, else None.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, jsonify({'error': 'Unauthorized: Missing token'}), 401

    id_token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid'], None, None
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None, jsonify({'error': 'Unauthorized: Invalid token'}), 401


@app.route('/')
def landing_page():
    """
    Render the landing page.

    Displays an index page with usage information for the API.

    Returns:
        str: Rendered HTML of the index page.
    """
    # Alter to be a usage for the api.
    return render_template("index.html")


@app.route('/api/f1', methods=['GET'])
def get_races():
    """
    Get all F1 race information.

    Verifies the Firebase token and returns race data in JSON format
    if the user is authenticated.

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with race data or error message.
            - int: HTTP status code.
    """
    uid, error_response, status = verify_firebase_token()
    if not uid:
        return error_response, status
    races = get_data("f1")
    return {"races":races,"count":len(races)}, 200


@app.route('/api/f1/<string:country_name>', methods=['GET'])
def get_country_races(country_name):
    """
    Get all F1 race information for a certain country.

    Verifies the Firebase token and returns race data in JSON format
    if the user is authenticated.

    Args:
        country_name (str): String of the country name to get all the races from. 

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with race data or error message.
            - int: HTTP status code.
    """
    uid, error_response, status = verify_firebase_token()
    if not uid:
        return error_response, status
    races = get_data("f1")
    results = []
    for race_info in races:
        if country_name.lower() == race_info.get('country', '').lower():
            results.append(race_info)
    if not results:
        return jsonify({'error': 'No races found for this country'}), 404
    return {"races":results,"count":len(results)}, 200


@app.route('/api/football/<string:team>', methods=['GET'])
def get_team_games(team):
    """
    Get all football games information for a given team.

    Verifies the Firebase token and returns race data in JSON format
    if the user is authenticated.

    Inputs:
        str: String of the team name.

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with football game data or error message.
            - int: HTTP status code.
    """
    uid, error_response, status = verify_firebase_token()
    if not uid:
        return error_response, status
    football_games = get_data("games")
    logos = get_data("logos")
    if team in football_games:
        return {"football":football_games[team],"count":len(football_games[team]), "team_base64":logos[team]}, 200
    else:
        jsonify({'error': 'No team found'}), 404


@app.route('/api/football', methods=['GET'])
def get_games():
    """
    Get all football games information.

    Verifies the Firebase token and returns race data in JSON format
    if the user is authenticated.

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with football game data or error message.
            - int: HTTP status code.
    """
    uid, error_response, status = verify_firebase_token()
    if not uid:
        return error_response, status
    football_games = get_data("games")
    return {"football":football_games,"count":len(football_games)}, 200



@app.route('/api/epic_games', methods=['GET'])
def get_epic_games():
    """
    Get all free epic games information.

    Verifies the Firebase token and returns race data in JSON format
    if the user is authenticated.

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with game data or error message.
            - int: HTTP status code.
    """
    uid, error_response, status = verify_firebase_token()
    if not uid:
        return error_response, status
    epic_games = get_data("epic_games")
    return {"epic_games":epic_games,"count":len(epic_games)}, 200


@app.errorhandler(404)
def page_not_found(e):
    """
    Return Error message upon unknown request.

    Returns:
        tuple: A tuple containing:
            - dict: JSON response with game data or error message.
            - int: HTTP status code.
    """
    if request.path.startswith('/api'):
        return jsonify({'error': 'Unknown API Request'}), 404
    return jsonify({'error': 'Unknown Request'}), 404

# Get data from the database.
initialize_firebase()
if __name__ == "__main__":
    app.run()
