import os

from flask import flash, request, url_for, render_template
from werkzeug.utils import secure_filename, redirect


# For a given file, return whether it's an allowed type or not
def allowed_file(app, filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def file_upload(app):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(app, file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('overview'))
        else:
            flash('Wrong File Type')
            return redirect(request.url)
    else:
        return render_template('add_file.html')


def delete_file(app, filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        os.remove(file)
    except OSError:
        flash('File does not exist')
