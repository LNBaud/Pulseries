from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

#Table de jointure entre User et Serie (quel user est abonné à quelle série)
watching = db.Table('watching',
                    db.Column('id_user', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                    db.Column('id_serie', db.Integer, db.ForeignKey('serie.id_serie'), primary_key=True))


#Utilisateurs
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    watching = db.relationship('Serie', secondary=watching, lazy='dynamic',
                               backref=db.backref('users', lazy='dynamic'))
    notifications_received = db.relationship('Notification', foreign_keys='Notification.id_recipient',
                                             backref='recipient', lazy='dynamic')
    last_notification_read_time = db.Column(db.DateTime) #datetime auquel l'utilisateur a lu ses notifications pour la dernière fois

    def __repr__(self):
        return (self.username)

    def set_password(self, password):
        '''Transforme le mot de passe donné en argument en un mot de passe crypté'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''Vérifie que le mot de passe indiqué est bien celui de l'utilisateur'''
        return check_password_hash(self.password_hash, password)

    def is_following(self, serie):
        '''Renvoie True si l'utilsateur est abonné à la série en argument, False sinon'''
        return (self.watching.filter(watching.c.id_serie == serie.id_serie).count() > 0)

    def follow(self, serie):
        '''Abonnement de l'utilisateur à la série'''
        if not self.is_following(serie):
            self.watching.append(serie)

    def unfollow(self, serie):
        '''Désabonnement de l'utilisateur de la série'''
        if self.is_following(serie):
            self.watching.remove(serie)

    def new_notifications(self):
        '''Renvoie les nouvelles notifications de l'utilisateur, 
        ie les notifications enregistrées depuis la dernière date de lecture des notifications'''
        last_read_time = self.last_notification_read_time or datetime(1900, 1, 1)
        return Notification.query.filter_by(recipient=self).filter(
            Notification.timestamp > last_read_time).count()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#Séries
class Serie(db.Model):
    id_serie = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    nb_season = db.Column(db.Integer)
    genre = db.Column(db.String(20))
    start_date = db.Column(db.String)
    url_picture_tvshow = db.Column(db.String)
    summary = db.Column(db.String)
    realisateur = db.Column(db.String(50))
    name_act = db.Column(db.String)
    status = db.Column(db.String(20))
    saisons = db.relationship('Saison', backref='serie', lazy='dynamic')

    def __repr__(self):
        return (self.name)

#Saisons
class Saison(db.Model):
    id = db.Column(db.String, primary_key=True)
    id_saison = db.Column(db.Integer)
    nb_episode = db.Column(db.Integer)
    episodes = db.relationship('Episode', backref='saison', lazy='dynamic')
    url_picture_season = db.Column(db.String)
    id_serie = db.Column(db.Integer, db.ForeignKey('serie.id_serie'), nullable=False)

    def __repr__(self):
        return ("Saison {} de la série {}.".format(self.id_saison, self.id_serie))

#Episodes
class Episode(db.Model):
    id = db.Column(db.String, primary_key=True)
    id_ep = db.Column(db.Integer)
    ep_name = db.Column(db.String(50))
    ep_sum = db.Column(db.Text)
    ep_date = db.Column(db.DateTime)
    id_saison = db.Column(db.Integer, db.ForeignKey('saison.id'))
    notifications = db.relationship('Notification', foreign_keys='Notification.id_episode', backref='episode',
                                    lazy='dynamic')

    def __repr__(self):
        return ("Episode {} de la saison {}".format(self.id_ep, self.id_saison))

#Notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_episode = db.Column(db.Integer, db.ForeignKey('episode.id'))
    id_recipient = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "Notification de l'épisode {0} pour l'utilisateur {1}".format(self.id_episode, self.id_recipient)

    def suppression(self):
        '''Supprime la notification de la base de données'''
        Notification.query.filter_by(id=self.id).delete()
        db.session.commit()

    def emailsending(self):
        '''Envoie un mail de notification à l'utilisateur'''
        print(self.recipient.email)
        liste_id=self.id_episode.split('-')
        serie = Serie.query.filter_by(id_serie = liste_id[0]).first()
        msg = MIMEMultipart()
        msg['From'] = 'pulseries2018@gmail.com'
        msg['To'] = self.recipient.email
        msg['Subject'] = 'Une nouvel épisode bientôt disponible !'
        message = "{} le nouvel épisode de {} sort le {}. Soyez prêt !".format(self.episode.ep_name, serie.name, self.episode.ep_date.strftime("%d-%m-%Y"))
        msg.attach(MIMEText(message))
        mailserver = smtplib.SMTP('smtp.gmail.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login('pulseries2018@gmail.com', 'Password2018')
        mailserver.sendmail('pulseries2018@gmail.com', self.recipient.email , msg.as_string())
        mailserver.quit()
