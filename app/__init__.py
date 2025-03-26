from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    
    # Configuration MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'WindowS2.0'
    app.config['MYSQL_DB'] = 'seahawks_nester'
    app.config['MYSQL_PORT'] = 3307
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app