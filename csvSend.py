#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gmailAPI as gmail
import csv
import unicodedata
import sys
import os

""" Envoie leurs notes aux étudiants

Attention à bien spécifier :
- notes : le fichier de notes (csv)
- scans : le dossier dans lequel trouver les scans à envoyer aux étudiants le cas échéant
- create_message(nom, prenom, champs) : le corps du mail
- subject : le sujet du mail
- delimiter : le séparateur utilisé dans le csv

Pour chaque ligne du fichier csv (en ignorant la première), le script va :
- récupérer l'adresse email
- récupérer nom/prénom
- fabriquer le texte du message
"""

sender = "alexis.flesch@utbm.fr"
subject = 'Note(s) mathématiques'
delimiter = ','


def create_message(nom, prenom, champs, data):
    """Crée le corps du mail générique qui sera envoyé
        Les paramètres accessibles sont :
        - nom : le nom de l'étudiant(e)
        - prenom : son prénom
        - champs : le nom des informations envoyées sous forme de liste ['CC1/10', 'CC2/10',...]
        - data : les données correspondantes aux champs ['7','8', ...]
    """

    message_text = "Bonjour,\n\n"
    message_text += "Ceci est un envoie automatique. Si vous pensez qu'il s'agit d'une "
    message_text += "erreur ou si vous constatez des informations erronées dans ce message, "
    message_text += "merci de m'en faire part par retour de mail.\n\n"
    message_text += 'Nom : ' + nom + '\n'
    message_text += 'Prénom : ' + prenom + "\n"
    for i in range(len(champs)):
        message_text += '  - ' + champs[i] + ' : ' + data[champs[i]] + '\n'
    message_text += '\n'
    message_text += "En cas de doute, où si vous pensez que les informations ci-dessus sont erronées, merci de m'en faire part par retour de mail.\n\n"
    message_text += "Cordialement,\n\n"
    message_text += "Alexis Flesch."
    return message_text


# Rien à modifier en-dessous de cette ligne !


def guessFileAndFolder():
    """Récupère les arguments donnés au script :
        - le premier : le fichier csv
        - le deuxième : le dossier avec les PJ (facultatif)
    """
    if len(sys.argv) == 1:
        print("Merci de spécifier le fichier de notes à traiter et éventuellement un dossier contenant des copies à mettre en PJ")
        sys.exit(0)
    elif len(sys.argv) == 2:
        notes = sys.argv[1]
        scansFolder = None
    else:
        notes = sys.argv[1]
        scansFolder = sys.argv[2]
    return notes, scansFolder


def asciify(s):
    """Supprime les accents et passe en minuscules
    Permet d'identifier automatiquement les champs "nom", "prénom" et "email" dans le csv
    qui peuvent être en majuscule, en minuscule, un peu des deux, avec ou sans accents...
    """
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('ascii').lower()


def compare(nom1, prenom1, nom2, prenom2):
    """Asciify et permute"""
    a = asciify(nom1)
    b = asciify(prenom1)
    c = asciify(nom2)
    d = asciify(prenom2)
    if (a, b) == (c, d) or (b, a) == (c, d):
        return True
    else:
        return False


def findAttachment(nom, prenom):
    """Cherche dans scanFolders (si non vide) des fichiers sous une des formes:
        - nom.prenom.pdf
        - prenom.nom.pdf
        - nom1.prenom1.nom2.prenom2.pdf
        - prenom1.nom1.nom2.prenom2.pdf
        - ...
    Utilise asciify pour supprimer les accents et les majuscules
    """
    for f in os.listdir(scansFolder):
        if os.path.isfile(os.path.join(scansFolder, f)):
            foo = f.split('.')
            # Le fichier n'est pas au bon format
            if not len(foo) % 2 or foo[-1] != 'pdf':
                continue
            nb = len(foo)//2  # nombre d'étudiants
            for i in range(nb):
                nom_i = asciify(foo[2*i])
                prenom_i = asciify(foo[2*i+1])
                if compare(nom, prenom, nom_i, prenom_i):
                    return f
    print("Scan non trouvé pour", nom, prenom, sep=' ')
    return None


def askFields(fields):
    """Repère les champs "nom", "prénom" et "email" puis demande
    à l'utilisateur les champs à renvoyer dans le corps du message
    """
    newFields = []
    nameField, firstNameField, emailField = False, False, False
    for f in fields:
        if asciify(f) == 'nom':
            nameField = f
        elif asciify(f) == 'prenom':
            firstNameField = f
        elif asciify(f) in ['mail', 'email']:
            emailField = f
        else:
            newFields.append(f)
    if not nameField:
        print("Attention ! Aucun champ 'nom' trouvé dans le fichier !")
    if not firstNameField:
        print("Attention ! Aucun champ 'prenom' trouvé dans le fichier !")
    if not emailField:
        print("Attention ! Aucun champ 'email' trouvé dans le fichier !")
        sys.exit(0)

    print("*"*100)
    print("Informations présentes dans le fichier: ")
    for i in range(len(newFields)):
        print(str(i+1), '. ', newFields[i])
    print("*"*100)
    num = input("Quelle(s) information(s) faut-il envoyer aux étudiants ? Donner une liste séparée par des virgules, sans espaces : 1,2,4,...\n")
    newFields = [newFields[int(i)-1] for i in num.split(',')]

    return nameField, firstNameField, emailField, newFields


def sendgrades(service, notes, scansFolder):
    with open(notes, newline='') as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=delimiter)
        fields = csvReader.fieldnames
        nameField, firstNameField, emailField, newFields = askFields(fields)

        k = 0
        for row in csvReader:
            nom = row[nameField]
            prenom = row[firstNameField]
            email = row[emailField]
            message_text = create_message(nom, prenom, newFields, row)
            if scansFolder:
                attachment = findAttachment(nom, prenom)
            else:
                attachment = None
            if k == 0:
                k = 1
                print(
                    "Avant d'envoyer massivement des emails, merci de vérifier que le message type ci-dessous vous convient :\n")
                print("*"*100)
                print(message_text)
                print("*"*100)
                print("Pièce jointe : ", attachment)
                print("*"*100)
                x = input("Continuer ? o/n ")
                if x == "n" or x == "no" or x == "non":
                    sys.exit(0)

            if attachment is not None:
                message = gmail.CreateMessageWithAttachment(
                    sender, email, subject, message_text, scansFolder, attachment)
            else:
                message = gmail.CreateMessage(
                    sender, email, subject, message_text)
            gmail.SendMessage(service, 'me', message)


if __name__ == '__main__':
    # On récupère le nom du csv et le dossier avec les copies
    notes, scansFolder = guessFileAndFolder()
    # On s'authentifie avec gmail
    service = gmail.authenticate()
    # On lance le script !
    sendgrades(service, notes, scansFolder)
