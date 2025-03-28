# Pollution Monitoring System

A community-driven air quality monitoring platform that empowers users to contribute and explore environmental data through interactive surveys and engaging visualizations.

## Features

- User authentication system (login/signup)
- Interactive air quality surveys
- Data visualization dashboard
- Environmental impact tracking
- Community participation tools

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Chart.js

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/pollution-monitoring-system.git
   cd pollution-monitoring-system
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Setup environment variables
   ```
   export DATABASE_URL=your_database_url
   ```

4. Run the application
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

## Usage

1. Register a new account or login with existing credentials
2. Complete the air quality survey to contribute data
3. Visit the dashboard to visualize collected data and trends
4. Explore air quality patterns and environmental insights

## License

[MIT](https://choosealicense.com/licenses/mit/)