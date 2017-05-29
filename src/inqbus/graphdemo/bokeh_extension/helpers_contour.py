import os
from glob import glob

import dask.array as da
import numpy as np
import scipy.ndimage as sc
import tables as tb
from bokeh.models import ColumnDataSource, Float
from inqbus.graphdemo.bokeh_extension.helpers import \
    binary_from_data_map
from inqbus.graphdemo.constants import (
    MAX_NUMBERS_DEFAULT,
    X_MAX_CONTOUR,
    Y_MAX_CONTOUR,
    Y_MIN_CONTOUR,
    X_MIN_CONTOUR,
    MAX_POINTS_CORRECTION, CONTOUR_DATA_SET)


def maxpoints_filter_matrix(matrix, numpoints_x, numpoints_y):
    """
    Minimize number of points to given numpoints
    :param numpoints_y: number of points wanted in y-direction
    :param numpoints_x: number of points wanted in x-direction
    :param matrix: matrix where points should be reduced
    """
    rows, columns = matrix.shape

    if columns == 0:
        columns = 1

    if rows == 0:
        rows = 1

    # clacluate factors to minimize points
    row_factor = float(numpoints_y * MAX_POINTS_CORRECTION) / float(rows)

    col_factor = float(numpoints_x * MAX_POINTS_CORRECTION) / float(columns)

    if row_factor > 1.0:
        row_factor = 1.0

    if col_factor > 1.0:
        col_factor = 1.0

    return sc.zoom(matrix, (row_factor, col_factor), order=3)


def range_filter(data, xmin, xmax, ymin, ymax):
    """
    Remove points which are not displayed in the given range
    """

    rows, columns = data.shape

    row_factor = float(rows) / Y_MAX_CONTOUR
    col_factor = float(columns) / X_MAX_CONTOUR

    row_min = max(int(ymin * row_factor), 0)
    row_max = min(int(ymax * row_factor), rows)
    col_min = max(int(xmin * col_factor), 0)
    col_max = min(int(xmax * col_factor), columns)

    data = data[row_min:row_max, col_min:col_max]

    return data

def clip(data, x_bin_min, x_bin_max, y_bin_min, y_bin_max):
    """
    Remove points which are not displayed in the given range
    """

    data = data[x_bin_min:x_bin_max, y_bin_min:y_bin_max]

    return data


def get_file_data(path,
                  plot_width=None,
                  plot_height=None,
                  x_min=None,
                  x_max=None,
                  y_min=None,
                  y_max=None):
    filenames = sorted(glob(CONTOUR_DATA_SET))

#        os.path.join(path,
#                                         '08',
#                                         '2015*_leipzig_CHM080079_000.h5')))

    if not filenames:
        n = 500
        x = np.linspace(0, 10, n)
        y = np.linspace(0, 10, n)
        xx, yy = np.meshgrid(x, y)
        z = np.sin(xx) * np.cos(yy)

    else:
        beta_raws = []
        times = []

        for fn in filenames:
            h5_file = tb.open_file(fn, 'r')

            signal_group = h5_file.get_node("/raw_signal")
            beta_raws.append(signal_group.beta_raw)
            times.append(signal_group.time)
        # ds = Dataset(fn)
        #    beta_raws.append( ds.variables['beta_raw'] )
        #    times.append( ds.variables['time'] )

        height = signal_group.height
        beta_raw_da_arrays = [da.from_array(beta_raw, chunks=(100, 100)) for
                              beta_raw in beta_raws]
        beta_raw_concat = da.concatenate(beta_raw_da_arrays, axis=0)

        time_da_arrays = [da.from_array(time, chunks=100) for time in times]
        time_concat = da.concatenate(time_da_arrays, axis=0)
        x = time_concat
        y = np.array(height)
        z = beta_raw_concat

#    x_min, x_max, y_min, y_max = clear_ranges(x_min, x_max, y_min, y_max)
    x0= x[0].compute()
    xN= x[-1].compute()

    if not x_min:
        x_min = x0
        x_bin_min = 0
    else:
        x_bin_min = int(x.shape[0]*(x0-x_min)/(x0-xN))
    if not x_max:
        x_max = xN
        x_bin_max = x.shape[0]-1
    else:
        x_bin_max = int(x.shape[0]*(x0-x_max)/(x0-xN))
    if not y_min:
        y_min = y[0]
        y_bin_min = 0
    else:
        y_bin_min = int(y.shape[0]*(y[0]-y_min)/(y[0]-y[-1]))
    if not y_max:
        y_max = y[-1]
        y_bin_max = y.shape[0]-1
    else:
        y_bin_max = int(y.shape[0]*(y[0]-y_max)/(y[0]-y[-1]))


#    z = range_filter(z, x_min, x_max, y_min, y_max)
    clipped = clip(z, x_bin_min, x_bin_max, y_bin_min, y_bin_max)


    if plot_height:
        plot_height = int(plot_height)
    else:
        plot_height = MAX_NUMBERS_DEFAULT

    if plot_width:
        plot_width = int(plot_width)
    else:
        plot_width = MAX_NUMBERS_DEFAULT

    gridded = maxpoints_filter_matrix(clipped, plot_width, plot_height)

    return x.compute(), y, gridded.astype('float64'), x_min, x_max, y_min, y_max

class ImageColumnDataSource(ColumnDataSource):
    """  """

    X0 = Float()
    Y0 = Float()
    DX = Float()
    DY = Float()

def get_data(path):
    """Just return hard coded data in directory 08 or render default
    example of bokeh-doku"""

    x, y, z, x_min, x_max, y_min, y_max  = get_file_data(path)

    data = ColumnDataSource(data=dict(
        image=[z],

    ))

    return data, x_min, x_max, y_min, y_max


def clear_ranges(x_min, x_max, y_min, y_max):
    """
    check if a range is given and if it is valid. If not use the defaults.
    """

    if x_min and float(x_min) >= X_MIN_CONTOUR:
        x_min = float(x_min)
    else:
        x_min = X_MIN_CONTOUR

    if x_max and float(x_max) <= X_MAX_CONTOUR:
        x_max = float(x_max)
    else:
        x_max = X_MAX_CONTOUR

    if y_max and float(y_max) <= Y_MAX_CONTOUR:
        y_max = float(y_max)
    else:
        y_max = Y_MAX_CONTOUR

    if y_min and float(y_min) >= Y_MIN_CONTOUR:
        y_min = float(y_min)
    else:
        y_min = Y_MIN_CONTOUR

    return x_min, x_max, y_min, y_max

def get_contour_data_binary(path, plot_width=None,
                            plot_height=None,
                            x_min=None,
                            x_max=None,
                            y_min=None,
                            y_max=None):
#    x_min, x_max, y_min, y_max = clear_ranges(x_min, x_max, y_min, y_max)

    x, y, z, x_min, x_max, y_min, y_max = get_file_data(path,
                            plot_width=plot_width,
                            plot_height=plot_height,
                            x_min=x_min,
                            x_max=x_max,
                            y_min=y_min,
                            y_max=y_max)

    shape = z.shape

    data_map = {
        'data.data.image': [z],
        'attributes.x_min': x_min,
        'attributes.x_max': x_max,
        'attributes.y_min': y_min,
        'attributes.y_max': y_max,
#        'data.data.x': [x_min],
#        'data.data.y': [y_min],
#        'data.data.dw': [x_max - x_min],
#        'data.data.dh': [y_max - y_min],
        'data._shapes.image': [shape],
    }

    bin_data = binary_from_data_map(data_map)

    return bin_data
