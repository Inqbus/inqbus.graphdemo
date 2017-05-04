from os import listdir
from os.path import isfile, join

from flask import render_template, url_for


def get_files_by_path(path):
    results = [f for f in listdir(path) if isfile(join(path, f))]
    return results


def get_files(app):
    files = []

    dir = app.config['UPLOAD_FOLDER']
    results = get_files_by_path(dir)

    for file in results:
        files.append({
            'file': file,
            'id': file,
            'delete_url': url_for('deletefile', filename=file)
        })
    return files


def overview_view_admin(app):
    data = {
        'files': get_files(app),
        'add_url': url_for('addfile')
    }
    return render_template('overview_admin.html', **data)


def overview_view(app):
    data = {
        'files': get_files(app),
        'add_url': url_for('addfile')
    }
    return render_template('overview.html', **data)
