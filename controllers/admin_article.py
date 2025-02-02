from flask import Blueprint, render_template, request, redirect, flash, current_app
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

# Create the Blueprint
admin_article = Blueprint('admin_article', __name__, template_folder='templates')

@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = '''
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
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('/admin/article/show_article.html', articles=articles)

@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image')

    filename = None
    if image and image.filename != '':
        filename = secure_filename('img_upload_' + str(int(2147483647 * random())) + '.png')
        image_path = os.path.join(current_app.root_path, 'static/images/', filename)
        image.save(image_path)

    try:
        sql = '''
        INSERT INTO cle_usb (nom_cle_usb, photo_url, prix_cle_usb, type_cle_usb_id, description)
        VALUES (%s, %s, %s, %s, %s)
        '''
        tuple_add = (nom, filename, prix, type_article_id, description)
        mycursor.execute(sql, tuple_add)
        get_db().commit()
        flash(u'Article ajouté avec succès', 'alert-success')
    except Exception as e:
        get_db().rollback()
        flash(u'Erreur lors de l\'ajout de l\'article: ' + str(e), 'alert-danger')

    return redirect('/admin/article/show')