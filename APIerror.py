class APIError(Exception):
    '''Erreur lors de la requête API'''

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return 'APIError : {}'.format(self.status)
