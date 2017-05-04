from bokeh import __version__ as bokeh_version
from bokeh.models import ColumnDataSource
from inqbus.graphdemo.bokeh_extension.helpers_contour import get_data
from inqbus.graphdemo.bokeh_extension.helpers_xy import get_diagram_data
from inqbus.graphdemo.bokeh_extension.layout import XYPlotJSLayout, \
    XYPlotPythonLayout, ContourPlotLayout
from inqbus.graphdemo.constants import UPLOAD_PATH


def build_xy_plot_js(upload_path, filename):
    """
    Prepare a plot using the XYPlotJSLayout and a hdf5-file as datasource.
    Returns everything for rendering the plot-layout.

    :param filename: File which should be used
    :param upload_path: path where to find files
    """

    source = ColumnDataSource()

    source.data = get_diagram_data(upload_path, filename)

    layout = XYPlotJSLayout(table_select=None,
                            x_axis=None,
                            y_axis=None,
                            plot=None,
                            data=source)

    script, div = layout.render_components()

    return {'script': script, 'div': div, 'version': bokeh_version}


def build_xy_plot_python():
    """
    Prepare a plot using the XYPlotPythonLayout and a selectable hdf5-file
    as datasource.
    Returns everything for rendering the plot-layout.
    """

    layout = XYPlotPythonLayout(table_select=None,
                                x_axis=None,
                                y_axis=None,
                                plot=None,
                                data=None)

    return layout.render_components()


def build_contour_plot(upload_path=UPLOAD_PATH):
    """
    Prepare a plot using the ContourPlotLayout and hdf5-files located in
    08-subdir.
    If no data is provided a default example is rendered.
    Returns everything for rendering the plot-layout.

    :param upload_path: path where to find files
    """
    data = get_data(upload_path)

    layout = ContourPlotLayout(
        data=data
    )

    return layout.render_components()
