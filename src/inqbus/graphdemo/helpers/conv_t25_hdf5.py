# helper file to convert .t25 files including table like
# "Datum"  "Zeit"  "SO2_43c = pmt = int.T = react.T = lampHz = lampV = pres = flow = kal_SO2 = so2_bkg =  so2_coef = Fluss_null = Fluss_kal"
# to hdf5

from glob import glob

import datetime
import time

import tables as tb


class DataTable(tb.IsDescription):
    # "Datum"  "Zeit"  "SO2_43c = pmt = int.T = react.T = lampHz = lampV = pres = flow = kal_SO2 = so2_bkg =  so2_coef = Fluss_null = Fluss_kal"
    date = tb.Int64Col(pos=1)
    SO2_43c = tb.Float64Col(pos=2)  # @UndefinedVariable
    pmt = tb.Float64Col(pos=3)  # @UndefinedVariable
    int_T = tb.Float64Col(pos=4)
    react_T = tb.Float64Col(pos=5)
    lampHz = tb.Float64Col(pos=6)
    lampV = tb.Float64Col(pos=7)
    pres = tb.Float64Col(pos=8)
    flow = tb.Float64Col(pos=9)
    kal_SO2 = tb.Float64Col(pos=10)
    so2_bkg = tb.Float64Col(pos=11)
    so2_coef = tb.Float64Col(pos=12)
    Fluss_null = tb.Float64Col(pos=13)
    Fluss_kal = tb.Float64Col(pos=14)


def read_nc_data(in_file):
    whole_data = []

    rootgrp = open(in_file, "r")
    for line in rootgrp.readlines():
        line.strip('\n')
        values = line.split(' ')
        # print(line)
        while '' in values:
            values.remove('')
        if len(values) != 16:
            continue
        try:
            values.remove('\n')
        except ValueError:
            continue

        result = []

        date = values.pop(0) + ' ' + values.pop(0)
        res = time.mktime(
            datetime.datetime.strptime(
                date, "%d.%m.%y %H:%M:%S").timetuple())

        result.append(int(res))
        for x in values:
            result.append(float(x))

        whole_data.append(result)

    print(len(whole_data))

    return whole_data


def get_table(out_file):

    pbl_group = out_file.create_group("/", 'data', 'data')
    table = tb.Table(pbl_group, 'PBL', description=DataTable)

    return table


def append_to_hdf_file(rec_data, out_file):

    outfile = tb.open_file(out_file, 'a')

    table = outfile.get_node("/data/PBL")

    table.append(rec_data)

    outfile.close()


in_files = sorted(glob('*.t25'))
out_file = "dwd.h5"
outfile = tb.open_file(out_file, 'w')
table = get_table(outfile)

for in_file in in_files:
    print (in_file)


    table.append(read_nc_data(in_file))

outfile.close()