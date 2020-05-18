from threading import Thread
import requests
from app.models import Serie,Saison, Episode
from sqlalchemy import update
from datetime import datetime
import time
from execution import PopulateDatabase

class UpdateDatabase(Thread, PopulateDatabase) :

    def __init__(self,id):
        PopulateDatabase.__init__(self)
        Thread.__init__(self)
        self.__id=id

    def run(self):
        
        '''Mise à jour de la base de données'''
        
        chaine1 = 'tv/' + str(self.__id)
        informations = self.requete_api(chaine1,'')
        new_nb_season = informations["number_of_seasons"]
        new_status = informations["status"]

        #On update l'objet
        update(Serie).where(Serie.id_serie == self.__id). \
            values(nb_season=new_nb_season,status=new_status)

        #On va updater la dernière saison de notre série
        season_to_update = informations["number_of_seasons"]
        dictionnaire_saison = self.get_information_saison(self.__id,season_to_update)
        # On update l'objet
        update(Saison).where(Saison.id == '{}-{}'.format(self.__id, season_to_update)). \
            values(nb_episode=dictionnaire_saison['nb_episode'])


        #On va updater les épisodes dont la date n'est pas encore passée
        for j in range(1, dictionnaire_saison['nb_episode'] + 1):
            id_to_update ='{}-{}-{}'.format(self.__id,season_to_update,j)
            episode_update = Episode.query.filter_by( id =id_to_update).first()
            if episode_update is not None :
                print(episode_update)
                date = episode_update.ep_date
                #On vérifie pour tous les épisodes de la saison si la date est passée
                if not date  or date > datetime.now() :
                    dictionnaire_episode = self.get_information_episode(self.__id, season_to_update, j)
                    #On update l'objet
                    update(Episode).where(Episode.id == '{}-{}-{}'.format(self.__id,season_to_update,j)). \
                        values(ep_date=dictionnaire_episode['ep_date'], ep_name=dictionnaire_episode['ep_name'], ep_sum=dictionnaire_episode['ep_sum'])

class DailyUpdate :

    '''Lancement journalier des threads de mise à jour'''

    def __init__(self):
        self.ThreadArray = []
        self.list_serie_update = Serie.query.filter_by(status='Returning Series').all()

    def maj_serie(self):
        for serie_to_update in self.list_serie_update:
            id = serie_to_update.id_serie
            self.ThreadArray.append(UpdateDatabase(id))

        #On lance les threads 5 par 5 pour ne pas depasser le nombre de requetes autorisées par l'API
        for k in range (len(self.list_serie_update)//5):
            for l in range (5):
                self.ThreadArray[l+k*5].start()
            for m in range (5):
                self.ThreadArray[m+k*5].join()
            time.sleep(5)