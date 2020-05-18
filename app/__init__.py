from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)
login.login_view ='login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models


#on va faire tourner une fonction qui popule la database avec 200 séries si la table Série est vide
from execution import PopulateDatabase

populate_database = PopulateDatabase()
populate_database.initialize_database()


#execution automatique de la fonction qui met à jour la base de donnée toutes les 24h
from apscheduler.schedulers.background import BackgroundScheduler
from majbdd import *

scheduler_maj = BackgroundScheduler()
daily_update = DailyUpdate()
scheduler_maj.add_job(func=daily_update.maj_serie, trigger="interval", hours = 15)
scheduler_maj.start()


#calcul automatique toutes les 24h des notification à pousser
from notification import NewNotification

scheduler_notif = BackgroundScheduler()
new_notif = NewNotification()
scheduler_notif.add_job(func=new_notif.calcul_notification, trigger="interval", hours = 24)
scheduler_notif.start()
