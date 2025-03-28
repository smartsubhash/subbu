from app import app, init_db

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(host="0.0.0.0", port=5000, debug=True)
