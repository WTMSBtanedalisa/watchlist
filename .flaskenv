FLASK_ENV=development
FLASK_APP=watchlist
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')