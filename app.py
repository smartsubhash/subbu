from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pandas as pd
from datetime import datetime
import os
import logging
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your_secret_key")  # For flash messages and session management

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
from models import db, User
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

# Load the air quality dataset
def load_air_quality_data():
    try:
        data = pd.read_csv('air_quality.csv')
        return data
    except Exception as e:
        logging.error(f"Error loading air quality data: {str(e)}")
        return pd.DataFrame()

# Global variable for data
air_quality_data = load_air_quality_data()

# Create or load survey responses
def load_survey_responses():
    try:
        if not os.path.exists('survey_responses.csv'):
            # Create a new CSV file with columns if it doesn't exist
            columns = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 
                      'C6H6(GT)', 'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 
                      'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH', 'Air Quality']
            survey_df = pd.DataFrame(columns=columns)
            survey_df.to_csv('survey_responses.csv', index=False)
            return survey_df
        else:
            return pd.read_csv('survey_responses.csv')
    except Exception as e:
        logging.error(f"Error loading survey responses: {str(e)}")
        return pd.DataFrame()

# Routes
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user:
        if check_password_hash(user.password_hash, password):
            login_user(user)
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Incorrect password, please try again.")
            return redirect(url_for('login'))
    else:
        flash("Username does not exist, please sign up.")
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash("Username already exists. Please choose another one.")
        else:
            # Create a new user with hashed password
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password)
            
            # Add new user to the database
            db.session.add(new_user)
            db.session.commit()
            
            flash("Sign up successful. Please log in.")
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/result')
@login_required
def result():
    # Retrieve the prediction result from the session
    category = session.get('prediction_result', 'No result available')
    
    # Clear the prediction result from the session after displaying it
    session.pop('prediction_result', None)
    
    return render_template('result.html', category=category)

@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
        
    # Define the survey questions
    questions = [
        {"question": "How much traffic do you experience?", "name": "traffic"},  # CO(GT)
        {"question": "How much car exhaust pollution is there?", "name": "car_exhaust"},  # PT08.S1(CO)
        {"question": "How bad is the air pollution?", "name": "air_pollution"},  # NMHC(GT)
        {"question": "How much pollution comes from industries?", "name": "industry_pollution"},  # C6H6(GT)
        {"question": "What is the level of vehicle emissions?", "name": "vehicle_emissions"},  # PT08.S2(NMHC)
        {"question": "How much nitrogen pollution is there?", "name": "nitrogen_pollution"},  # NOx(GT)
        {"question": "How much ozone pollution is present?", "name": "ozone_pollution"},  # PT08.S3(NOx)
        {"question": "What is the overall pollution level?", "name": "pollution_level"},  # NO2(GT)
        {"question": "How much does the weather affect pollution?", "name": "weather_effect"},  # PT08.S4(NO2)
        {"question": "How severe is the fog/smog?", "name": "fog_smog"},  # PT08.S5(O3)
        {"question": "How bad is the pollution during rush hour?", "name": "rush_hour_pollution"}  # T
    ]

    # Track the current question
    current_question = int(session.get('current_question', 0))

    if request.method == 'POST':
        if 'previous' in request.form:
            # Move to the previous question
            if current_question > 0:
                session['current_question'] = current_question - 1
            return redirect(url_for('survey'))
        else:
            # Save the answer to the current question
            answer = request.form.get(questions[current_question]["name"])
            if answer is not None:
                session[f"answer_{current_question}"] = float(answer)  # Store the user-defined answer as float

            # If it is the last question, process the data and make prediction
            if current_question == len(questions) - 1:
                # Ensure no None values before making prediction
                responses = {f"answer_{i}": session.get(f"answer_{i}") for i in range(len(questions))}
                
                try:
                    # Calculate the total sum of responses
                    total_sum = sum(float(responses[f"answer_{i}"]) for i in range(len(questions)))

                    # Determine the category based on the total sum
                    if total_sum <= 20:
                        category = "Very Good"
                    elif total_sum <= 40:
                        category = "Good"
                    elif total_sum <= 60:
                        category = "Average"
                    elif total_sum <= 80:
                        category = "Poor"
                    else:
                        category = "Very Poor"

                    # Store the prediction result in the session
                    session['prediction_result'] = category

                    # Prepare data to be saved to the survey responses CSV
                    new_data = {
                        'Date': datetime.now().strftime("%d-%m-%Y"),
                        'Time': datetime.now().strftime("%H:%M:%S"),
                        'CO(GT)': responses['answer_0'],  # Traffic
                        'PT08.S1(CO)': responses['answer_1'],  # Car Exhaust
                        'NMHC(GT)': responses['answer_2'],  # Air Pollution
                        'C6H6(GT)': responses['answer_3'],  # Industry Pollution
                        'PT08.S2(NMHC)': responses['answer_4'],  # Vehicle Emissions
                        'NOx(GT)': responses['answer_5'],  # Nitrogen Pollution
                        'PT08.S3(NOx)': responses['answer_6'],  # Ozone Pollution
                        'NO2(GT)': responses['answer_7'],  # Overall Pollution Level
                        'PT08.S4(NO2)': responses['answer_8'],  # Weather Effect
                        'PT08.S5(O3)': responses['answer_9'],  # Fog/Smog
                        'T': responses['answer_10'],  # Rush Hour Pollution
                        'RH': 0.0,  # Default value for RH
                        'AH': 0.0,  # Default value for AH
                        'Air Quality': category  # Store the category in the Air Quality column
                    }

                    # Load existing survey responses
                    survey_df = load_survey_responses()

                    # Convert the new_data dictionary to a DataFrame
                    new_data_df = pd.DataFrame([new_data])

                    # Concatenate the new data with the existing DataFrame
                    survey_df = pd.concat([survey_df, new_data_df], ignore_index=True)

                    # Save the updated DataFrame back to the CSV file
                    survey_df.to_csv('survey_responses.csv', index=False)

                    flash(f"Survey submitted! Air Quality: {category}")
                except Exception as e:
                    flash(f"Error processing data: {str(e)}")
                
                # Clear the session data for the survey responses
                for i in range(len(questions)):
                    session.pop(f"answer_{i}", None)
                session.pop('current_question', None)
                
                return redirect(url_for('result'))  # Redirect to the result page
            else:
                # Move to the next question
                session['current_question'] = current_question + 1
                return redirect(url_for('survey'))

    # Display the current question
    question = questions[current_question]
    next_button_text = "Submit" if current_question == len(questions) - 1 else "Next"
    previous_button_disabled = current_question == 0
    
    return render_template('survey.html', 
                           question=question, 
                           next_button_text=next_button_text, 
                           previous_button_disabled=previous_button_disabled, 
                           current_question=current_question)

@app.route('/dashboard')
@login_required
def dashboard():
    
    # Load the survey responses for visualization
    try:
        survey_df = pd.read_csv('survey_responses.csv')
        
        # Count Air Quality categories for pie chart
        quality_counts = survey_df['Air Quality'].value_counts().to_dict()
        
        # Calculate average pollutant values for bar chart
        pollutants = ['CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)', 'PT08.S2(NMHC)', 
                     'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T']
        avg_pollutants = {col: float(survey_df[col].mean()) for col in pollutants}
        
        # Get recent submissions for the table
        recent_submissions = survey_df.tail(10).to_dict('records')
        
        return render_template('dashboard.html', 
                               quality_counts=json.dumps(quality_counts),
                               avg_pollutants=json.dumps(avg_pollutants),
                               recent_submissions=recent_submissions)
    except Exception as e:
        flash(f"Error loading dashboard data: {str(e)}")
        return render_template('dashboard.html', 
                               quality_counts=json.dumps({}),
                               avg_pollutants=json.dumps({}),
                               recent_submissions=[])

@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    
    try:
        survey_df = pd.read_csv('survey_responses.csv')
        quality_counts = survey_df['Air Quality'].value_counts().to_dict()
        return jsonify(quality_counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    # Log the user out with Flask-Login
    logout_user()
    # Also clear session variables
    session.pop('username', None)
    session.pop('current_question', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))
