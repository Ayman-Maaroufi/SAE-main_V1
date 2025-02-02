#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                          template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()
    sql = '''DROP TABLE IF EXISTS utilisateur, type_cle_usb, etat, cle_usb, commande, ligne_commande, panier, liste_envies, historique, adresse'''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE utilisateur(
        id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
        login VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        nom VARCHAR(255) NOT NULL
    ) DEFAULT CHARSET utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO utilisateur (login, email, password, role, nom) VALUES
    ('admin', 'admin@example.com', 'sha256$dPL3oH9ug1wjJqva$2b341da75a4257607c841eb0dbbacb76e780f4015f0499bb1a164de2a893fdbf', 'ROLE_admin', 'Admin'),
    ('client', 'client@example.com', 'sha256$1VZPRk0zlaQYUVxK$0de4e0b1b0d00c2a2c95e8b8e0d75d0e6b5a5d9d9d9d9d9d9d9d9d9d9d9d9d9d', 'ROLE_client', 'Client'),
    ('client2', 'client2@example.com', 'sha256$dPL3oH9ug1wjJqva$2b341da75a4257607c841eb0dbbacb76e780f4015f0499bb1a164de2a893fdbf', 'ROLE_client', 'Client2')
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE type_cle_usb(
        id_type_cle_usb INT AUTO_INCREMENT PRIMARY KEY,
        libelle_type_cle_usb VARCHAR(255) NOT NULL
    ) DEFAULT CHARSET utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO type_cle_usb (libelle_type_cle_usb) VALUES
    ('USB 2.0'),
    ('USB 3.0'),
    ('USB-C')
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE etat (
        id_etat INT AUTO_INCREMENT PRIMARY KEY,
        libelle VARCHAR(50) NOT NULL
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO etat (libelle) VALUES
    ('en cours de traitement'),
    ('expédié'),
    ('validé')
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE cle_usb (
        id_cle_usb INT AUTO_INCREMENT PRIMARY KEY,
        nom_cle_usb VARCHAR(255) NOT NULL,
        prix_cle_usb DECIMAL(10, 2) NOT NULL,
        capacite_id INT NOT NULL,
        type_cle_usb_id INT NOT NULL,
        stock INT NOT NULL,
        image VARCHAR(255),
        FOREIGN KEY (type_cle_usb_id) REFERENCES type_cle_usb(id_type_cle_usb)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO cle_usb (nom_cle_usb, prix_cle_usb, capacite_id, type_cle_usb_id, stock, image) VALUES
    ('SanDisk Ultra 32GB', 12.99, 32, 1, 100, 'sandisk_ultra.jpg'),
    ('Kingston DataTraveler 64GB', 15.99, 64, 2, 75, 'kingston_datatraveler.jpg'),
    ('Samsung BAR Plus 128GB', 29.99, 128, 3, 50, 'samsung_bar_plus.jpg')
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE commande (
        id_commande INT AUTO_INCREMENT PRIMARY KEY,
        date_achat DATE NOT NULL,
        utilisateur_id INT NOT NULL,
        etat_id INT NOT NULL,
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (etat_id) REFERENCES etat(id_etat)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES
    (NOW(), 2, 1),
    (NOW(), 3, 2)
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE ligne_commande(
        commande_id INT NOT NULL,
        cle_usb_id INT NOT NULL,
        prix DECIMAL(10, 2) NOT NULL,
        quantite INT NOT NULL,
        PRIMARY KEY (commande_id, cle_usb_id),
        FOREIGN KEY (commande_id) REFERENCES commande(id_commande),
        FOREIGN KEY (cle_usb_id) REFERENCES cle_usb(id_cle_usb)
    );
    '''
    mycursor.execute(sql)
    sql = '''
    INSERT INTO ligne_commande (commande_id, cle_usb_id, prix, quantite) VALUES
    (1, 1, 12.99, 2),
    (1, 2, 15.99, 1),
    (2, 3, 29.99, 3)
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE panier (
        utilisateur_id INT NOT NULL,
        cle_usb_id INT NOT NULL,
        quantite INT NOT NULL,
        date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, cle_usb_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (cle_usb_id) REFERENCES cle_usb(id_cle_usb)
    );
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE liste_envies (
        utilisateur_id INT NOT NULL,
        cle_usb_id INT NOT NULL,
        date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, cle_usb_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (cle_usb_id) REFERENCES cle_usb(id_cle_usb)
    );
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE historique (
        utilisateur_id INT NOT NULL,
        cle_usb_id INT NOT NULL,
        date_consultation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, cle_usb_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (cle_usb_id) REFERENCES cle_usb(id_cle_usb)
    );
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE adresse (
        id_adresse INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(255) NOT NULL,
        rue VARCHAR(255) NOT NULL,
        code_postal VARCHAR(10) NOT NULL,
        ville VARCHAR(255) NOT NULL,
        utilisateur_id INT NOT NULL,
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur)
    );
    '''
    mycursor.execute(sql)

    get_db().commit()
    return redirect('/')