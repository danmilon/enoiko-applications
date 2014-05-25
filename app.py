# -*- coding: utf-8 -*-

from glob import glob
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='', static_folder='')

cur_dir = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(cur_dir, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

xwria = {
    'mousiko': u'Μουσικό',
    'kouzina': u'Κουζίνα',
    'praktikis-oikologias-mellisokomoi': u'Πρακτικής Οικολογίας | Μελισσοκόμοι',
    'praktikis-oikologias-kalliergites': u'Πρακτικής Οικολογίας | Καλλιεργητές',
    '8erapeutiko-paraskeuastes': u'Θεραπευτικό | Παρασκευαστές',
    '8erapeutiko-8erapeutes': u'Θεραπευτικό | Θεραπευτές',
    'xeirotexnias-keramika': u'Χειροτεχνίας | Κεραμικά',
    'xeirotexnias-kosmimata': u'Χειροτεχνίας | Κοσμήματα',
    'xeirotexnias-xeirotexnies': u'Χειροτεχνίας | Χειροτεχνίες'
}

xwria_names = sorted(xwria.keys())

@app.route('/')
def index():
    if 'success' in request.args:
        success = True
    else:
        success = False

    return render_template('index.html',
                           xwria=xwria,
                           xwria_names=xwria_names,
                           success=success)

@app.route('/download/<xwrio>/<uuid>')
def download(xwrio, uuid):
    xwrio_dir = os.path.join(UPLOAD_FOLDER, xwrio)
    file_path = glob(os.path.join(xwrio_dir, uuid + '_*'))
    if len(file_path) != 1:
        return 'none or more than one files found'

    file_path = file_path[0]
    file_path = os.path.relpath(file_path, cur_dir)
    extension = file_path[file_path.rfind('.') + 1:]

    response = app.send_static_file(file_path)
    content_disposition = 'attachment; filename=%s.%s' % (uuid, extension)
    response.headers['Content-Disposition'] = content_disposition

    return response

@app.route('/download_photo/<uuid>/<index>')
def download_photo(uuid, index):
    file_path = glob(os.path.join(
        UPLOAD_FOLDER,
        'photos',
        '%s_%s.*' % (uuid, index)
    ))

    if len(file_path) != 1:
        return 'δεν υπαρχει η φωτογραφια'

    file_path = file_path[0]
    file_path = os.path.relpath(file_path, cur_dir)

    response = app.send_static_file(file_path)

    return response



@app.route('/list/<xwrio>')
def list(xwrio):
    if xwrio not in xwria:
        return 'invalid %s' % xwrio

    xwrio_dir = os.path.join(UPLOAD_FOLDER, xwrio)
    files = os.listdir(xwrio_dir)
    applications = []

    for file in files:
        onoma = file[37:file.rfind('.')]
        uuid = file[:36]

        photos = glob(os.path.join(UPLOAD_FOLDER, 'photos', uuid) + '_*')
        photo_urls = [url_for('download_photo', uuid=uuid, index=i) for i in range(len(photos))]

        applications.append({
            'onoma': onoma,
            'file_url': url_for('download', xwrio=xwrio, uuid=uuid),
            'photo_urls': photo_urls
        })

    return render_template('list.html',
                           applications=applications,
                           xwrio=xwria[xwrio])

@app.route('/apply', methods=['POST'])
def apply():
    for arg in ['xwrio', 'onoma']:
        if arg not in request.form:
            return 'invalid request'

    xwrio = request.form['xwrio']
    onoma = request.form['onoma']

    if 'file' not in request.files:
        return 'missing file'

    if onoma == '':
        return u'Το όνομα είναι άδειο'

    file = request.files['file']
    if file.filename == '':
        return u'δεν εχετε επιλεξει το αρχειο της αιτησης'

    photo_index = 1
    photo_files = []
    while True:
        photo_file = request.files.get('photo%s' % photo_index, None)
        if (photo_file is None) or (photo_file.filename == ''):
            break

        photo_files.append(photo_file)
        photo_index += 1

    if xwrio not in xwria:
        return 'invalid %s' % xwrio

    id = str(uuid.uuid4())
    extension = file.filename[file.filename.rfind('.') + 1:]
    filename = secure_filename('%s_%s.%s' % (id, onoma, extension))

    out_dir = os.path.join(app.config['UPLOAD_FOLDER'], xwrio)
    file.save(os.path.join(out_dir, filename))

    photo_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
    for i, photo_file in enumerate(photo_files):
        extension = photo_file.filename[photo_file.filename.rfind('.') + 1:]
        file_path = os.path.join(photo_dir, '%s_%s.%s' %(id, i, extension))
        photo_file.save(file_path)

    return redirect('/?success=1')


if __name__ == "__main__":
    app.run()
