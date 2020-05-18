from datetime import datetime, timedelta
from app.models import Episode, watching, Notification
from app import db
from sqlalchemy import delete

class NewNotification:

    def __init__(self):
        self.__notification_date = datetime.now() + timedelta(days=1)
        self.__supression_date = datetime.now() - timedelta(days=7)
        #On récupère tous les couples (user, serie favorite)
        self.__serie_fav = db.session.query(watching).all()

    def calcul_notification(self) :
        
        '''On récupère les épisodes qui vont sortir dans moins de 1 jour parmi nos séries favorites'''

        for i in self.__serie_fav :
            id_serie_notif = str(i[1])+"-"
            #Filtre sur la date de sortie de l'épisode et l'ID de la série correpondante
            episode_list = Episode.query.filter(Episode.ep_date.between(datetime.now(),self.__notification_date) & Episode.id.startswith(id_serie_notif)).all()
            for episode in episode_list :
                print(episode)
                #On crée une notification pour chaque couple (user abonné à la série, nouvel épisode de la série)
                notification = Notification(id_episode=episode.id, id_recipient=i[0])
                db.session.add(notification)
                db.session.commit()
                #On envoie un mail à l'utilisateur pour le prévenir
                notification.emailsending()

        #On supprime les notif datant de plus d'une semaine
        to_delete = Notification.query.filter(Notification.timestamp < self.__supression_date).all()
        for notif in to_delete:
            notif.suppression()
        db.session.remove()

