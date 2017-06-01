import os

import pandas as pd
import tables as tb
from inqbus.graphdemo.bokeh_extension.helpers import \
    binary_from_data_map, get_strides_avg_and_std, get_strides_avg, \
    get_max_value, get_min_value
from inqbus.graphdemo.constants import MAX_NUMBERS_DEFAULT, \
    REMOVE_DUPLICATES, X_AXIS_DATES, USE_DATA_FILTER, COLUMN_FOR_DATAFILTER
from tables import open_file


def read_hdf5_structure(h5file):
    """
    read all table-nodes from a hdf5-file
    :param h5file:
    :return:
    """
    nodes = {}
    for node in h5file:
        path = node._v_pathname
        if isinstance(node, tb.Table):
            nodes[path] = node
    return nodes


def get_columns(table):
    """
    get columnnames from hdf5-table
    :param table:
    :return:
    """

    df = pd.DataFrame.from_records(table[:])
    columns = df.to_dict(orient='list')

    return columns


def maxpoints_filter(df, numpoints):
    """
    Minimize number of points to given numpoints
    """
    x = df['x']
    y = df['y']

    x_averages = get_strides_avg(numpoints, x)
    y_averages, y_std = get_strides_avg_and_std(numpoints, y)

    return pd.DataFrame({'x': x_averages,
                         'y': y_averages,
                         'y_error_above': y_averages + y_std,
                         'y_error_below': y_averages - y_std})


def get_column_data(table,
                    plot_width=None,
                    plot_height=None,
                    x_min=None,
                    x_max=None,
                    y_min=None,
                    y_max=None,
                    x_column=None,
                    y_column=None,
                    data_filter=None):

    # get data from hdf5-table-node
    df = pd.DataFrame.from_records(table[:])

    if USE_DATA_FILTER and data_filter and (COLUMN_FOR_DATAFILTER in df):
        floated_filter = []
        for number in data_filter.split(','):
            floated_filter.append(float(number))

        df = df[df[COLUMN_FOR_DATAFILTER].isin(floated_filter)]

    # select columns which are selected by th plot
    if x_column and y_column and (x_column in df) and (y_column in df):
        df_x = df[x_column]
        df_y = df[y_column]

        df = pd.DataFrame({'x': df_x, 'y': df_y})
    else:
        # no or wrong columns selected return empty default
        df = pd.DataFrame({'x': [], 'y': []})
        return df

    # because bokeh clacluates on ms and unixtimestamp is on seconds
    if X_AXIS_DATES:
        df['x'] = df['x'] * 1000

    # filter values which ar not in given range if a rang is given
    if x_min and (x_min != 'NaN'):
        df = df[(df['x'] >= float(x_min))]

    if x_max and (x_max != 'NaN'):
        df = df[(df['x'] <= float(x_max))]

    df = df.sort_values(by='x')

    # minimize number of points to reduce data

    max_numbers = MAX_NUMBERS_DEFAULT
    if plot_width:
        max_numbers = int(plot_width)
    elif plot_height and plot_width and int(plot_height) > int(plot_width):
        max_numbers = int(plot_height)
    elif plot_height:
        max_numbers = int(plot_height)

    if max_numbers:
        df = maxpoints_filter(df, max_numbers)

    # remove duplicates to reduce data
    if REMOVE_DUPLICATES:
        df = df.drop_duplicates()

    return df


def get_diagram_data(upload_path, filename):
    """
    Read data-structure from a hdf5 file and provide it in a dictionary fitting
    DataSource.
    Data describes the hdf5-file-structure and is used fro the selectboxes
    """
    path = os.path.join(upload_path, filename)
    file = open_file(path, mode="r")

    data = {}

    tables = read_hdf5_structure(file)

    for table_path in tables:
        table_node = tables[table_path]
        columns = get_columns(table_node)
        for column_name in columns:
            if table_path not in data:
                data[table_path] = []
            data[table_path].append(column_name)

    file.close()
    return data


def get_python_plot_data(data,
                         xmin=None,
                         xmax=None,
                         ymin=None,
                         ymax=None,
                         x='x',
                         y='y',
                         y_error_above='y_error_above',
                         y_error_below='y_error_below',
                         y_col=None,
                         x_col=None):
    """
    Gets data as pandas dateframe and returns a dictionary with all
    data needed for drawing the plot
    """

    # get data of selected columns, convert them to numpy arrays and store them
    # in dictionary
    x_data = data[x].as_matrix()
    y_data = data[y].as_matrix()
    if y_error_above in data:
        y_above = data[y_error_above].as_matrix()
    else:
        y_above = y_data
    if y_error_below in data:
        y_below = data[y_error_below].as_matrix()
    else:
        y_below = y_data

    data_map = {
        'source.data.x': x_data,
        'source.data.index': x_data,
        'source.data.y': y_data,
        'source.data.y_above': y_above,
        'source.data.y_below': y_below,
    }

    # calculate ranges

    x_max = 10.0
    x_min = 0.0
    y_max = 10.0
    y_min = 0.0

    # TODO when calculating ranges add a little extra

    if x_data.size > 0 and (xmax == 'NaN' or xmax is None):
        # no maximum was provided so get the maximum in x-data
        x_max = get_max_value(x_data, default=x_max)
    elif xmax:
        # use given max-value
        x_max = float(xmax)
    # else use default x_max = 10

    if x_data.size > 0 and (xmin == 'NaN' or xmin is None):
        x_min = get_min_value(x_data, default=x_min)
    elif xmin:
        x_min = float(xmin)

    if y_data.size > 0 and (ymax == 'NaN' or ymax is None):
        y_max = get_max_value(y_data, default=y_max)
    elif ymax:
        y_max = float(ymax)
    if y_data.size > 0 and (ymin == 'NaN' or ymin is None):
        y_min = get_min_value(y_data, default=y_min)
    elif ymin:
        y_min = float(ymin)

    # min and max have to be different for drawing ranges
    if x_max == x_min:
        x_max = x_max + 0.5
        x_min = x_min - 0.5

    if y_max == y_min:
        y_max = y_max + 0.5
        y_min = y_min - 0.5

    data_map['plot.x_range.start'] = x_min
    data_map['plot.x_range.end'] = x_max
    data_map['plot.y_range.start'] = y_min
    data_map['plot.y_range.end'] = y_max

    return data_map


def get_file_data(upload_path, filename, table_path, **kwargs):
    # TODO optimize

    # read data from file
    path = os.path.join(upload_path, filename)
    file = open_file(path, mode="r")

    tables = read_hdf5_structure(file)

    table_node = tables[table_path] or None

    # default if data was not found
    data = pd.DataFrame({'x': [], 'y': []})

    if table_node:
        # data from selected table in file
        data = get_column_data(table_node, **kwargs)

    file.close()

    return data


def get_plot_data_binary(app, upload_path, filename, table_path, **kwargs):
    """
    Prepare data for js-callbacks with binary protocoll
    """

    data = get_file_data(upload_path, filename, table_path, **kwargs)

    xmin = kwargs['x_min']
    xmax = kwargs['x_max']
    ymin = kwargs['y_min']
    ymax = kwargs['y_max']

    x_col = kwargs['x_column']
    y_col = kwargs['y_column']

    # calculate binary plot-data
    binary = get_plot_binary_data(app, data, xmin=xmin, xmax=xmax, ymin=ymin,
                                  ymax=ymax, x_col=x_col, y_col=y_col)

    return binary


def get_plot_data_python(upload_path, filename, tablepath,
                         x_col=None, y_col=None, xmin=None,
                         xmax=None, ymin=None, ymax=None,
                         plotwidth=None, plotheight=None):
    """
    Prepare data for python-callbacks
    """

    data = get_file_data(upload_path, filename, tablepath,
                         plot_width=plotwidth,
                         plot_height=plotheight,
                         x_min=xmin,
                         x_max=xmax,
                         y_min=ymin,
                         y_max=ymax,
                         x_column=x_col,
                         y_column=y_col)

    python_data = get_python_plot_data(data,
                                       xmin=xmin,
                                       xmax=xmax,
                                       ymin=ymin,
                                       ymax=ymax,
                                       x='x',
                                       y='y',
                                       y_error_above='y_error_above',
                                       y_error_below='y_error_below',
                                       y_col=y_col,
                                       x_col=x_col)

    return python_data


def get_plot_binary_data(app,
                         data,
                         xmin=None,
                         xmax=None,
                         ymin=None,
                         ymax=None,
                         x='x',
                         y='y',
                         y_error_above='y_error_above',
                         y_error_below='y_error_below',
                         y_col=None,
                         x_col=None):

    data_map = get_python_plot_data(data,
                                    xmin=xmin,
                                    xmax=xmax,
                                    ymin=ymin,
                                    ymax=ymax,
                                    x=x,
                                    y=y,
                                    y_error_above=y_error_above,
                                    y_error_below=y_error_below,
                                    y_col=y_col,
                                    x_col=x_col)

    all_data = binary_from_data_map(data_map)

    return all_data
