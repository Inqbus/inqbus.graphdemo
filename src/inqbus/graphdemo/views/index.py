from os import listdir
from os.path import isfile, join

from flask import url_for, render_template

from inqbus.graphdemo import constants as c


def get_static_views():
    links = []
    views = c.STATIC_VIEWS
    for view in views:
        link = {
            'title': view,
            'path': url_for(view)
        }
        links.append(link)
    return links


def get_hdf5_file_views(app):
    views = c.FILE_RELATED_VIEWS
    links = []

    # results = DB.session.query(Paths.file).all()

    file = app.config['UPLOAD_FOLDER']

    results = [f for f in listdir(file) if isfile(join(file, f))]

    for file in results:
        for view in views:
            link = {
                'title': view + ': ' + file,
                'path': url_for(view, filename=file)
            }
            links.append(link)
    return links


def getLinks(app):
    return get_static_views() + get_hdf5_file_views(app)


def index_view(app):
    data = {
        'links': getLinks(app),
    }
    return render_template('index.html', **data)
