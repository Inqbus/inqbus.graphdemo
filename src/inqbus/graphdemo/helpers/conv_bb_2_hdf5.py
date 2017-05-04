from netCDF4 import Dataset
import numpy as np
import tables as tb
from glob import glob

import sys

MISSING_PBL = -1


def read_nc_data(in_file):

    rootgrp = Dataset(in_file, "r", format="NETCDF4")

    time_axis = rootgrp.variables['time']
    height_axis = rootgrp.variables['range']

    beta_raw = np.array(rootgrp.variables['beta_raw'])

    result = {'time': np.array(time_axis),
              'height': np.array(height_axis),
              'beta_raw': np.array(beta_raw)}

#    data_float = data_np.astype(float)

#    data_float[data_np== MISSING_PBL ] = np.NaN

    return result


def create_hdf_file(data_tables, out_file):

    outfile = tb.open_file(out_file, 'w')

    signal_group = outfile.create_group("/", 'raw_signal', 'Raw signal')

    for name, data in data_tables.items():

        if not data.dtype.fields:
            desc = np.dtype([(name, 'f8')])
        else:
            desc = data.dtype

        table = tb.Array(signal_group, name, data)

#        table.append(data)

    outfile.close()

# def append_to_hdf_file( rec_data, out_file):
#
#    outfile = tb.open_file(out_file, 'a')
#
#    table = outfile.get_node("/pbl/PBL")
#
#    table.append(rec_data)
#
#    outfile.close()


in_files = sorted(glob('*_leipzig_CHM080079_000.nc'))


for in_file in in_files:
    out_file = '.'.join(in_file.split('.')[:-1]) + ".h5"
    create_hdf_file(read_nc_data(in_file), out_file)
