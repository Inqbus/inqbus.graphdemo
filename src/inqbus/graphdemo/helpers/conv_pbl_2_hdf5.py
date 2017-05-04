from netCDF4 import Dataset
import numpy as np
import tables as tb
from glob import glob

import sys

MISSING_PBL = -1


def read_nc_data(in_file):

    rootgrp = Dataset(in_file, "r", format="NETCDF4")

    time_axis = rootgrp.variables['time']

    data_np = np.array(rootgrp.variables['pbl'])

    data_float = data_np.astype(float)

    data_float[data_np == MISSING_PBL] = np.NaN

    data = np.rec.fromarrays(
        data_float.T, dtype=[
            ('Layer1', float), ('Layer2', float), ('Layer3', float)])

    from numpy.lib.recfunctions import append_fields

    whole_data = append_fields(data, 'time', time_axis)

    return whole_data


def create_hdf_file(rec_data, out_file):

    outfile = tb.open_file(out_file, 'w')

    pbl_group = outfile.create_group("/", 'pbl', 'Planetary boundary layer')
    table = tb.Table(pbl_group, 'PBL', description=rec_data.dtype)

    table.append(rec_data)

    outfile.close()


def append_to_hdf_file(rec_data, out_file):

    outfile = tb.open_file(out_file, 'a')

    table = outfile.get_node("/pbl/PBL")

    table.append(rec_data)

    outfile.close()


in_files = sorted(glob('PBL_*_hohenpeissenberg.nc'))


for in_file in in_files:
    out_file = '.'.join(in_file.split('.')[:-1]) + ".h5"
    create_hdf_file(read_nc_data(in_file), out_file)
