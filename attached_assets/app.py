from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages and session management

# SQLite database setup
def get_db_connection():
    conn = sqlite3.connect('users.db')  # Create/Connect to SQLite database
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

# Initialize the database (only need to run once)
def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT)')
    conn.commit()
    conn.close()

# Load your dataset (not used for prediction anymore)
data = pd.read_csv('air_quality.csv')  # Replace with your dataset path
print(data.columns)  # To check the columns in your dataset

@app.route('/', methods=['GET'])
def home():
    if 'username' not in session:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))  # If not logged in, redirect to login
    return render_template('home.html')  # Load home.html after login

@app.route('/login', methods=['GET'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))  # If already logged in, redirect to home
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user:
        if user['password'] == password:
            session['username'] = username  # Store the logged-in user's username in the session
            flash("Login successful!")
            return redirect(url_for('home'))  # Redirect to the home page (root route)
        else:
            flash("Incorrect password, please try again.")
            return redirect(url_for('login'))  # Reload the login page
    else:
        flash("Username does not exist, please sign up.")
        return redirect(url_for('login'))  # Reload the login page

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username already exists in the database
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            flash("Username already exists. Please choose another one.")
        else:
            # Add new user to the database
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            conn.close()
            flash("Sign up successful. Please log in.")
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/result')
def result():
    # Retrieve the prediction result from the session
    category = session.get('prediction_result', 'No result available')
    
    # Clear the prediction result from the session after displaying it
    session.pop('prediction_result', None)
    
    return render_template('result.html', category=category)

@app.route('/survey', methods=['GET', 'POST'])
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

                    # Check if the survey_responses.csv file exists
                    if not os.path.exists('survey_responses.csv'):
                        # Create a new CSV file with columns if it doesn't exist
                        columns = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 
                                   'C6H6(GT)', 'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 
                                   'NO2(GT)', 'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH', 'Air Quality']
                        survey_df = pd.DataFrame(columns=columns)
                        survey_df.to_csv('survey_responses.csv', index=False)

                    # Read the existing survey responses
                    survey_df = pd.read_csv('survey_responses.csv')

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
    
    return render_template('survey.html', question=question, next_button_text=next_button_text, previous_button_disabled=previous_button_disabled, current_question=current_question)

@app.route('/logout')
def logout():
    # Log the user out by clearing the session
    session.pop('username', None)
    session.pop('current_question', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True)