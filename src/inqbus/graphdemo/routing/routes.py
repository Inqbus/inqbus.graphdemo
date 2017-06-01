from flask import redirect, url_for, request, render_template
from flask_login import current_user
from flask_menu import register_menu
# from flask_security import login_required, roles_required
from flask_security.views import logout
from inqbus.graphdemo.bokeh_extension.builder import build_contour_plot
from inqbus.graphdemo.constants import TABLE_URL_KEY
from inqbus.graphdemo.views.diagram import (
    diagram_view,
    diagram_data_view,
    diagram_plot_data_view,
    diagram_contour_data_view,
    diagram_overview_view)
from inqbus.graphdemo.views.index import index_view
from inqbus.graphdemo.views.manage_files import delete_file, file_upload
from inqbus.graphdemo.views.overview import overview_view, \
    overview_view_admin


def admin_views(app):
    @app.route('/deletefile/<path:filename>')
    # @roles_required('admin')
    def deletefile(filename):
        delete_file(app, filename)
        return redirect(url_for('overview'))

    @app.route('/addfile', methods=['GET', 'POST'])
    # @roles_required('admin')
    def addfile():
        # form = AddPathForm()
        # if form.validate_on_submit():
        #     file = form.file.data
        #     store_file(file)
        #     return redirect(url_for('overview'))
        # return render_template('add_file.html',
        #                        title='Sign In',
        #                        form=form)
        return file_upload(app)


def logged_in_views(app):
    @app.route('/')
    # @login_required
    @register_menu(app, '.home', 'Home', order=0)
    def index():
        return index_view(app)

    @app.route('/diagram_overview')
    # @login_required
    @register_menu(app, '.diagram_overview', 'XY-Plots', order=1)
    def diagram_overview():
        return diagram_overview_view(app)

    @app.route('/overview')
    # @login_required
    @register_menu(app, '.overview', 'File overview', order=2)
    def overview():
        # if current_user.has_role('admin'):
        #     return overview_view_admin(app)
        return overview_view_admin(app)

    @app.route('/diagramview/<path:filename>')
    # @login_required
    def diagramview(filename):
        return diagram_view(app, filename)

    @app.route('/diagramview/<path:filename>/data', methods=('GET', 'POST'))
    # @login_required
    def diagramdataview(filename):
        upload_path = app.config['UPLOAD_FOLDER']

        table = request.form[TABLE_URL_KEY] or None
        plot_width = request.form['plot_width'] or None
        plot_height = request.form['plot_height'] or None
        x_min = request.form['x_min'] or None
        x_max = request.form['x_max'] or None
        y_min = request.form['y_min'] or None
        y_max = request.form['y_max'] or None
        x_column = request.form['x_column'] or None
        y_column = request.form['y_column'] or None
        y_column2 = request.form['y_column2'] or None
        data_filter = request.form['data_filter'] or None

        if table:
            return diagram_plot_data_view(app,
                                          upload_path,
                                          filename,
                                          table,
                                          plot_width=plot_width,
                                          plot_height=plot_height,
                                          x_min=x_min,
                                          x_max=x_max,
                                          y_min=y_min,
                                          y_max=y_max,
                                          x_column=x_column,
                                          y_column=y_column,
                                          data_filter=data_filter,
                                          y_column2=y_column2)

        return diagram_data_view(app, upload_path, filename)

    @app.route('/logout')
    # @login_required
    @register_menu(app, 'logout', 'Logout', order=100)
    def logoutview():
        return logout()

    # using the bocket socket does not work properly
    # @app.route('/bokeh_socket')
    # @login_required
    # @register_menu(
    #     app,
    #     '.bokeh_socket',
    #     'Diagram View using Bokeh-Socket',
    #     order=1)
    # def bokehsocketview():
    #     script = autoload_server(model=None, url=BOKEH_URL + '/sliders')
    # return render_template('bokeh_server.html', bokeh_script=script,
    # url=BOKEH_URL)
    @app.route('/contourplot')
    @register_menu(app, '.contourplot', 'Contourplot', order=1)
    # @login_required
    def contourplot():
        upload_path = app.config['UPLOAD_FOLDER']
        script, div = build_contour_plot(upload_path)
        data = {
            'file': '',
            'chart': {
                'script': script,
                'div': div,
            },
            'debug': app.config['DEBUG']
        }
        return render_template('diagram.html', **data)

    @app.route('/contourplot/data', methods=['GET', 'POST'])
    # @login_required
    def contourplot_data():
        path = app.config['UPLOAD_FOLDER']

        plot_width = request.form['plot_width'] or None
        plot_height = request.form['plot_height'] or None
        x_min = request.form['x_min'] or None
        x_max = request.form['x_max'] or None
        y_min = request.form['y_min'] or None
        y_max = request.form['y_max'] or None

        return diagram_contour_data_view(app, path,
                                         plot_width=plot_width,
                                         plot_height=plot_height,
                                         x_min=x_min,
                                         x_max=x_max,
                                         y_min=y_min,
                                         y_max=y_max)


def anonymous_views(app):
    @app.route('/')
    def index_login():
        redirect(url_for('login'))


def set_up_routes(app):
    admin_views(app)
    logged_in_views(app)
    anonymous_views(app)
