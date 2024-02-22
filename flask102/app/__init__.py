from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import Config
from flask_login import LoginManager


app = Flask(__name__)
load_dotenv()
app.config.from_object(Config)
db = SQLAlchemy()
Migrate(app, db)
db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'


from app import routes, models, errors