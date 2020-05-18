"""Ce fichier présente une class qui nous permet de remplir la base de données. Soit lors de son initialisation à
travers la méthode initialize_database, soit lors de la mise à jour de la base de donnée (cf fichier majbdd.py) """

import requests
from app import app, db
from app.models import Serie, Saison, Episode
from APIerror import APIError
from datetime import datetime


class PopulateDatabase :

    def __init__(self):
        self.__list_id_serie = []
        self._urlapi = 'https://api.themoviedb.org/3/'
        self._key = '?api_key=6eb3c7e954300012802d8c3edfd095fd&language=fr-FR'

    def requete_api(self,chaine1,chaine2):
        '''Requête à l'API'''
        url = self._urlapi + chaine1 + self._key + chaine2
        resultat = requests.get(url).json()
        #Exception si l'API renvoie une erreur
        if 'status_code' in resultat.keys() and resultat['status_code'] not in (1, 12, 13):  #codes de réussite
            raise APIError(resultat['status_message'])
        return resultat

    def __get_serie_id (self):
        '''Récupération des id des 200 séries les plus populaires'''
        chaine1='discover/tv'
        for j in range(1, 11):
            chaine2= '&sort_by=vote_count.desc&page=' + str(j)
            resultat = self.requete_api(chaine1,chaine2)
            for i in range(20):
                id_serie = resultat["results"][i]["id"]
                self.__list_id_serie.append(id_serie)
        return self.__list_id_serie

    def get_information_serie(self, id):
        '''Récupération des informations sur une série'''
        chaine1 = 'tv/' + str(id)
        informations = self.requete_api(chaine1,'')
        dictionnaire = {}
        dictionnaire['id_serie'] = id
        dictionnaire['name'] = informations["name"]
        dictionnaire['nb_season'] = informations["number_of_seasons"]
        dictionnaire['genre'] = informations["genres"][0]["name"]
        dictionnaire['start_date'] = informations["first_air_date"]
        dictionnaire['summary'] = informations["overview"]
        dictionnaire['realisateur'] = 'None'
        if len(informations["created_by"]) != 0:
            dictionnaire['realisateur'] = informations["created_by"][0]["name"]
        if not informations["poster_path"]:
            dictionnaire[
                "url_picture_tvshow"] = "http://www.51allout.co.uk/wp-content/uploads/2012/02/Image-not-found.gif"
        else:
            dictionnaire['url_picture_tvshow'] = "https://image.tmdb.org/t/p/w300" + informations["poster_path"]
        dictionnaire['status'] = informations["status"]

        # Recuperation du nom des acteurs en faisant une nouvelle requete
        chaine1_acteur= 'tv/'+ str(id) + '/credits'
        info_act = self.requete_api(chaine1_acteur, '')
        dictionnaire['name_act'] = ''
        if len(info_act["cast"]) > 0:
            dictionnaire['name_act'] += info_act["cast"][0]["name"]
            for i in range(1, len(info_act["cast"])):
                dictionnaire['name_act'] += ', ' + info_act["cast"][i]["name"]
        return dictionnaire
        

    def get_information_saison(self, id_serie, id_saison):
        '''Récupération des informations sur une saison'''
        chaine1 = "tv/{}/season/{}".format(id_serie,id_saison)
        informations_season = self.requete_api(chaine1,'')
        dictionnaire = {}
        if not informations_season["poster_path"]:
            dictionnaire["url_picture_season"] = "http://www.51allout.co.uk/wp-content/uploads/2012/02/Image-not-found.gif"
        else:
            dictionnaire['url_picture_season'] = "https://image.tmdb.org/t/p/w300" + informations_season["poster_path"]
        dictionnaire['nb_episode'] = len(informations_season["episodes"])
        return dictionnaire
        

    def get_information_episode(self, id_serie, id_saison, id_episode):
        '''Récupération des informations sur un épisode'''
        chaine1 = 'tv/{}/season/{}/episode/{}'.format(id_serie,id_saison,id_episode)
        informations_ep = self.requete_api(chaine1,'')
        dictionnaire = {}
        dictionnaire['ep_sum'] = None
        if "overview" in informations_ep.keys():
            dictionnaire['ep_sum'] = informations_ep["overview"]
        dictionnaire['ep_name'] = None
        if "name" in informations_ep.keys():
            dictionnaire['ep_name'] = informations_ep["name"]
        dictionnaire['ep_date'] = None
        if "air_date" in informations_ep.keys() and informations_ep["air_date"]:
            dictionnaire['ep_date'] = datetime.strptime(informations_ep["air_date"], '%Y-%m-%d')
        return dictionnaire

    def add_in_database(self,objet):
        '''Ajout à la base de données'''
        db.session.add(objet)
        db.session.commit()


    def initialize_database(self):
        
        '''Remplissage de la base de données'''
        
        #On vérifie si la database est déjà remplie en regardant si on a déjà une série dedans
        if Episode.query.first() is None :
            for i in range(200):
                dictionnaire_episode = {}
                id = self.__list_id_serie[i]

                #On créé l'objet dans la base de données
                dictionnaire_serie = self.get_information_serie(id)
                serie = Serie(id_serie=dictionnaire_serie['id_serie'],name=dictionnaire_serie['name'],nb_season=dictionnaire_serie['nb_season'],genre=dictionnaire_serie['genre'],start_date=dictionnaire_serie['start_date'],summary=dictionnaire_serie['summary'],
                              realisateur=dictionnaire_serie['realisateur'],name_act=dictionnaire_serie['name_act'],url_picture_tvshow=dictionnaire_serie['url_picture_tvshow'],status=dictionnaire_serie['status'])
                self.add_in_database(serie)

                #On parcourt ensuite les saisons de la série
                for i in range (1, dictionnaire_serie['nb_season']+1):
                    dictionnaire_saison = self.get_information_saison(id,i)

                    #On crée les objets associés dans la base de données
                    saison = Saison (id='{}-{}'.format(dictionnaire_saison['id_serie'],dictionnaire_saison['id_saison']), id_saison = dictionnaire_saison['id_saison'],
                                     id_serie=dictionnaire_saison['id_serie'], nb_episode = dictionnaire_saison['nb_episode'],url_picture_season= dictionnaire_saison['url_picture_season'])
                    self.add_in_database(saison)

                    #On parcourt les épisodes de la saison
                    for j in range (1,dictionnaire_saison['nb_episode'] + 1) :
                        dictionnaire_episode = self.get_information_episode(id,i,j)
                        #On crée les objets associés dans la base de données
                        episode= Episode(id='{}-{}-{}'.format(dictionnaire_episode['id_serie'], dictionnaire_episode['id_saison'], dictionnaire_episode['id_ep']), id_ep=dictionnaire_episode['id_ep'],
                                         ep_name= dictionnaire_episode['ep_name'], ep_date=dictionnaire_episode['ep_date'], ep_sum=dictionnaire_episode['ep_sum'], id_saison= dictionnaire_episode['id_saison'])
                        self.add_in_database(episode)
            db.session.remove()

