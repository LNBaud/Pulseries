from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Serie, Saison, Episode, watching, Notification
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, redirect, url_for, request
from sqlalchemy import func
from datetime import datetime, timedelta
import notification

# Vue de la page d'accueil
@app.route('/')
@app.route('/index')
def index():
    #On requête 3 séries aléatoires parmi la base de données
    serie_aleatoire = Serie.query.order_by(func.random()).limit(3).all()
    return render_template('index.html', title='Home', series = serie_aleatoire)
    

# Vue de la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    #Si l'utilisateur est déjà connecté, on le redirige vers la page d'accueil
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Connexion', form=form)

# Déconnexion de l'utilsateur. On est directement retournés vers l'accueil.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Vue de la page d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    #Si l'utilisateur est déjà connecté, on le redirige vers la page d'accueil
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Inscription', form=form)


# Vue de la page de profil
@app.route('/profile')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def profile():
    #On requête les séries auxquelles l'utilisateur est abonné
    series = Serie.query.join(watching, (watching.c.id_serie == Serie.id_serie)).filter(watching.c.id_user == current_user.id).all()
    return render_template('profil.html', title='Profil', series=series)


# Vue de la recherche de séries
@app.route('/recherche-serie', methods=['POST'])
@app.route('/recherche-serie/', methods=['POST'])
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def recherche_nominative():
    search = request.form["nom-serie"]
    genre = request.form ["genre"]
    # Recherche des séries par nom uniquement
    if genre == "Tous" :
        resultats = Serie.query.filter(Serie.name.like("%{}%".format(search))).order_by(Serie.name).all()
    #Recherche des séries par nom et par genre
    else :
        resultats = Serie.query.filter(Serie.name.like("%{}%".format(search)), Serie.genre.like("%{}%".format(genre))).order_by(
            Serie.name).all()
    return render_template('resultats_recherche.html',query = search, resultats=resultats)


# Vue de l'ensemble des séries disponibles
@app.route('/recherche-alphabetique/')
def recherche_alphabetique():
    resultats = Serie.query.order_by(Serie.name).all()
    return render_template('resultats_recherche.html', resultats=resultats)

# Vue de la page série
@app.route('/serie/<id_serie>')
@app.route('/serie/<id_serie>/')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def serie(id_serie):
    serie = Serie.query.filter_by(id_serie = id_serie).first_or_404()
    #Saisons de la série
    saisons = Saison.query.filter_by(id_serie = id_serie)
    return render_template('serie.html', serie=serie, saisons=saisons, title='Serie')

# Vue de la page saison
@app.route('/serie/<id_serie>/saison/<id_saison>')
@app.route('/serie/<id_serie>/saison/<id_saison>/')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def saison(id_serie, id_saison):
    saison = Saison.query.filter_by(id_serie=id_serie, id_saison=id_saison).first_or_404()
    serie = Serie.query.filter_by(id_serie=id_serie).first_or_404()
    #Episodes de la saison
    nb_episodes = saison.nb_episode
    episodes = [0 for i in range(nb_episodes)]
    for i in range (nb_episodes) :
        id_ep = id_serie + "-" + id_saison + "-" + str(i+1)
        episodes[i] = Episode.query.filter_by(id = id_ep).first()
    return render_template('saison.html', serie=serie, saison=saison, episodes = episodes,title='Saison')
    
# Abonnement à une série
@app.route('/follow/<id_serie>')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def follow_serie(id_serie):
    serie = Serie.query.get(id_serie)
    current_user.follow(serie)
    db.session.commit()
    return redirect(url_for('serie', id_serie=id_serie))

# Désabonnement à une série
@app.route('/unfollow/<id_serie>')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def unfollow_serie(id_serie):
    serie = Serie.query.get(id_serie)
    current_user.unfollow(serie)
    db.session.commit()
    return redirect(url_for('serie', id_serie=id_serie))

@app.route('/unfollow2/<id_serie>')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def unfollow_serie_profile(id_serie):
    serie = Serie.query.get(id_serie)
    current_user.unfollow(serie)
    db.session.commit()
    return redirect(url_for('profile'))

#Recherche de nouvelles notifications
@app.route('/refresh_notifications')
@login_required
def refresh_notifications():
    episode_list = Episode.query.filter(
        Episode.ep_date.between(datetime.now(), datetime.now() + timedelta(days=1))).all()
    for i in range (len(episode_list)) :
        id_total = episode_list[i].id.split('-')
        id_serie = int(id_total[0])
        if not current_user.is_following(Serie.query.get(id_serie)) :
            current_user.follow(Serie.query.get(id_serie))
    db.session.commit()
    new_notif = notification.NewNotification()
    new_notif.calcul_notification()
    return redirect(url_for('profile'))

# Vue des notifications
@app.route('/notifications')
@login_required #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def notifications():
    # On met à jour dans la base de donnée la date à laquelle l'utilisateur a vu ses notifications pour la dernière fois
    # Cela permettra de faire la disctinction entre les nouvelles notifications et les anciennes notifications déjà vues
    current_user.last_notification_read_time = datetime.utcnow()
    db.session.commit()
    notifications = current_user.notifications_received.order_by(Notification.timestamp.desc()).all()
    series = [0 for i in range (len(notifications))]
    for i in range (len(notifications)) :
        id_serie = notifications[i].id_episode.split('-')
        series[i] = Serie.query.filter_by(id_serie= id_serie[0]).first()
    notif_serie = [0 for i in range (len(notifications))]
    for i in range (len(notifications)) :
        notif_serie[i] = ((notifications[i],series[i]))
    print (notif_serie)
    return render_template('notifications.html', notif_serie = notif_serie)
