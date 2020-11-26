# Envoi automatique de mails
Pour envoyer automatiquement les informations contenues dans un fichier csv (un mail par ligne, avec ajout éventuel de pièce jointe).

But premier : envoyer massivement et de manière individuelle les notes à un (ou plusieurs) contrôles à des étudiant(e)s. Le cas échéant, ajouter une version numérique des copies corrigées.


## Configuration initiale

### Activation de l'API
Rendez-vous sur 
https://console.developers.google.com/apis pour activer l'API et télécharger le fichier `credentials.json` (à placer dans le même dossier que ce programme, google peut vous l'avoir donné sous un autre nom).

### Modification du message générique
Dans le script principal (`csvSend.py`), il y a quatre choses à renseigner :
- sender : votre adresse mail
- subject : l'objet du mail
- delimiter : le séparateur utilisé dans le csv
- `create_message(nom, prenom, champs, data)` : fonction qui écrit le corps de l'email

Dans l'idéal ces éléments sont renseignés une fois pour toute avec un message suffisamment générique pour s'adapter à toutes les situations.

## Lancement du script

### Sans pièce jointe
On lance le script en donnant en argument le chemin vers le fichier csv :

`python3 csvSend.py chemin/vers/fichier.csv`


### Avec pièce jointe

On lance le script en donnant en argument le chemin vers le fichier csv et le chemin du dossier contenant les pièces jointes :

`python3 csvSend.py chemin/vers/fichier.csv chemin/dossier/pj`

### Glisser-déposer

On peut aussi glisser-déposer le chemin d'accès dans un terminal avec un navigateur de fichiers, cela a pour effet d'ajouter des quotes mais elles sont ignorées par le terminal :

`python3 csvSend.py 'chemin/vers/fichier.csv' 'chemin/dossier/pj' `

Attention cependant : la manière dont le terminal envoie l'information au script peut varier d'un shell à l'autre. Sur une configuration "standard", les quotes sont ignorées. Si ce n'est pas le cas, on peut modifier la fonction `guessFileAndFolder` pour enlever les quotes (avec `foo.replace("'","")` par exemple).

## Le script en détails

### Colonnes recherchées par le script
nom, prénom, email

Les deux premières sont facultatives, la troisième ne l'est pas. Le script ignore les majuscules et les accents pour repérer les colonnes en question. Les champs "nom" et "prénom" peuvent être utilisés dans le corps du message.


### Informations qui seront envoyées

Le script permet de choisir les colonnes à envoyer. Le message envoyé est personnalisable via la fonction `message`.


### Pièce jointe

On peut demander au script d'ajouter une pièce jointe. Celle-ci doit être sous une des formes:
- nom.prenom.pdf
- nom1.prenom1.nom2.prenom2.pdf
- nom1.prenom1.nom2.prenom2.....nomn.prenomn.pdf

Les champs nom et prenom peuvent être inversés. Cela permet d'envoyer le même scan à deux étudiants qui ont travaillé en binôme dès que le fichier pdf est bien formaté.