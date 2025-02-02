# controllers/client_article.py

from flask import Blueprint, render_template
from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                           template_folder='templates')

@client_article.route('/admin/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    sql = """
    SELECT
        cle_usb.id_cle_usb,
        cle_usb.nom_cle_usb,
        capacite.libelle_capacite,
        cle_usb.description,
        cle_usb.prix_cle_usb,
        type_cle_usb.libelle_type_cle_usb
    FROM
        cle_usb
    JOIN
        capacite ON cle_usb.capacite_id = capacite.id_capacite
    JOIN
        type_cle_usb ON cle_usb.type_cle_usb_id = type_cle_usb.id_type_cle_usb
    """
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)