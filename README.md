**Pulseries**

********

Notre site comprend les fonctionnalités suivantes :
- Liste des séries disponibles
- Recherche par genre/nom des séries (uniquement si le client est loggé)
- Une page par série, et par saison de série (si user loggé uniquement), avec une possibilité de s'abonner/se désabonner
- Une page profil par utilisateur avec un aperçu des séries suivies, et possibilité de se désabonner
- Notifications sur le site et envoyées par mail
- Test de nouvelles notifications sur la page profil (attention : un peu lent mais ne pas appuyer plusieurs fois)

Pour démarrer :
- Soit sur Pycharm :
    - Ouvrez le dossier pulseries en projet
    - Créez un nouvel environnement virtuel
    - Suivez les instructions pour installer les modules de requirements.txt
    - Lancez le projet
- Soit avec l'invite de commande :
    - Allez dans le dossier global du projet (pulseries)
    - Créez un environnement virtuel
    - Exécutez : pip install -r requirements.txt
    - Exécutez : export FLASK_APP=siteweb.py (pour Windows, remplacez export par set)
    - Exécutez : flask run
    - Dans le navigateur : http://localhost:5000/

Actions à effectuer pour tester notre site :
- Créer un nouvel utilisateur (indiquez une véritable adresse mail pour recevoir les notifications) 
- Abonnez-vous à vos séries préférées
- Pour tester les notifications, cliquez sur le bouton "TEST NOUVELLES NOTIFICATIONS" sur la page de votre profil, qui vous abonnera aux séries dont un épisode sort le lendemain, et fasse une mise à jour de la table notifications (attention, la fonction pouvant prendre quelques secondes, n'appuyez qu'une seule fois pour ne pas recevoir les mails en double ou plus)
- Recherchez les séries que vous voulez, avec ou sans genre

User existant : 
- admin : id : admin, mdp : admin

Attention : la base de données est déjà incluse dans le dossier. Si vous la supprimez :
- Allez dans le dossier global du projet (pulseries)
- Supprimez le dossier migrations également
- Exécutez : export FLASK_APP=siteweb.py (pour Windows, remplacez export par set)
- Exécutez : flask db init
- Exécutez : flask db migrate
- Exécutez : flask db upgrade
- Ensuite, vous pourrez de nouveau lancer le site

REMARQUE : Reremplir la base de données prend environ 3h (dû au volume de données)
