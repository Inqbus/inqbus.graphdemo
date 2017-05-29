from flask import render_template, jsonify, url_for
from flask.wrappers import Response
from inqbus.graphdemo.bokeh_extension.helpers_contour import \
    get_contour_data_binary
from inqbus.graphdemo.bokeh_extension.helpers_xy import get_diagram_data, \
    get_plot_data_binary
from inqbus.graphdemo.bokeh_extension.builder import build_xy_plot_js
from inqbus.graphdemo.views.index import get_hdf5_file_views


def diagram_view(app, filename):
    link = url_for('diagramdataview', filename=filename)
    upload_path = app.config['UPLOAD_FOLDER']
    data = {
        'file': filename,
        'chart': build_xy_plot_js(upload_path, filename),
        'debug': app.config['DEBUG']
    }
    return render_template('diagram.html', **data)


def diagram_data_view(app, upload_path, filename):

    app.logger.info(
        "Requested diagram_data_view for %s/%s" %
        upload_path, filename)

    data = get_diagram_data(upload_path, filename)

    return jsonify(data)


def diagram_plot_data_view(app, upload_path, filename, table_path, **kwargs):

    app.logger.info("Requested data from %s/%s:%s with kwargs %s" %
                    (upload_path,
                     filename,
                     table_path,
                     kwargs)
                    )

    binary_data = get_plot_data_binary(
        app, upload_path, filename, table_path, **kwargs)

    resp = Response(binary_data, mimetype='application/octet-stream')

    return resp

def validate_range(kwargs):
    x_min_str = kwargs['x_min']
    x_max_str = kwargs['x_max']
    y_min_str = kwargs['y_min']
    y_max_str = kwargs['y_max']
    if not x_min_str:
        x_min = None
    else:
        x_min = float(x_min_str)
    if not x_max_str:
        x_max = None
    else:
        x_max = float(x_max_str)
    if not y_min_str:
        y_min = None
    else:
        y_min = float(y_min_str)
    if not y_max_str:
        y_max = None
    else:
        y_max = float(y_max_str)
    return x_min, x_max, y_min, y_max

def validate_resolution(kwargs):
    return int(kwargs['plot_width']), int(kwargs['plot_height'])


def diagram_contour_data_view(app, upload_path, **kwargs):

    app.logger.info("Requested data from %s with kwargs %s" %
                    (upload_path,
                     kwargs)
                    )

    x_min, x_max, y_min, y_max = validate_range(kwargs)
    plot_width, plot_height = validate_resolution(kwargs)

    binary_data = get_contour_data_binary(upload_path, plot_width, plot_height, x_min, x_max, y_min, y_max )

    resp = Response(binary_data, mimetype='application/octet-stream')

    return resp


def diagram_overview_view(app):
    data = {
        'links': get_hdf5_file_views(app),
    }
    return render_template('index.html', **data)
