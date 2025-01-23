import datetime

# Dictionnaire de traduction des mois
MOIS = {
    'January': 'janvier',
    'February': 'février',
    'March': 'mars',
    'April': 'avril',
    'May': 'mai',
    'June': 'juin',
    'July': 'juillet',
    'August': 'août',
    'September': 'septembre',
    'October': 'octobre',
    'November': 'novembre',
    'December': 'décembre'
}

# Obtenir la date
date = datetime.datetime.now()
jour = date.strftime("%d")
mois = MOIS[date.strftime("%B")]
annee = date.strftime("%Y")

# Gérer le cas particulier du 1er
if jour == '01':
    jour = '1er'

# Afficher la date
print(f"{jour} {mois} {annee}")
