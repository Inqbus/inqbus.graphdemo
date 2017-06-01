import json

import numpy as np
from inqbus.graphdemo.constants import SPECIAL_JS_TYPES


def get_binary_and_json_metadata_for_attr(attribute, data):
    """
    Create metadata and binary data for binary protocoll
    :param data: data which should be stored in the attribute
    :param attribute: name/path of the attribute in JS
    """
    metadata = {
        'length': '0',
        'type': 'unknown',
        'attribute': attribute,
    }
    bin_data = get_binary_data_for_obj(data)
    if isinstance(data, float):
        metadata['type'] = 'float'
        bin_data = get_binary_data_for_obj(str(data))
        metadata['length'] = str(len(bin_data))
    elif isinstance(data, int):
        metadata['type'] = 'int'
        bin_data = get_binary_data_for_obj(str(data))
        metadata['length'] = str(len(bin_data))
    elif isinstance(data, str):
        if data in SPECIAL_JS_TYPES:
            metadata['type'] = data
            metadata['length'] = str(len(bin_data))
        else:
            metadata['type'] = 'string'
            metadata['length'] = str(len(bin_data))
    elif isinstance(data, np.ndarray):
        metadata['type'] = 'floatlist'
        metadata['length'] = str(len(bin_data))
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], np.ndarray):

        metadata['type'] = 'contourdata'
        metadata['length'] = str(len(bin_data))
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], float):
        metadata['type'] = 'contourattr'
        metadata['length'] = str(len(bin_data))
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], tuple) and (len(data[0]) == 2):
        metadata['type'] = 'contourshape'
        metadata['length'] = str(len(bin_data))
    else:
        pass
    return bin_data, metadata


def get_binary_data_for_obj(data):
    """
    Get binary data depending on datatype
    :param data:
    :return:
    """
    bin_data = bytearray()

    if isinstance(data, str):
        bin_data = bytearray(data, 'utf8')
    elif isinstance(data, np.ndarray):
        bin_data = bytearray(memoryview(data).tobytes())
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], np.ndarray):
        data_to_send = data[0]
        bin_data = bytearray(memoryview(data_to_send).tobytes())
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], float):
        bin_data = bytearray(str(data[0]), 'utf8')
    elif isinstance(data, list) and (len(data) == 1) and \
            isinstance(data[0], tuple) and (len(data[0]) == 2):
        bin_data_str = "%s;%s" % data[0]
        return get_binary_data_for_obj(bin_data_str)
    else:
        pass
    return bin_data


def binary_from_data_map(data_map):
    meta_data = {}
    binary_data = bytearray()

    for attribute in data_map.keys():
        bin_data, json_metadata = get_binary_and_json_metadata_for_attr(
            attribute,
            data_map[attribute]
        )
        meta_data[attribute] = json_metadata
        meta_data[attribute]['offset'] = len(binary_data)
        binary_data += bin_data

    json_data = json.dumps(meta_data)
    json_data_bytes = get_binary_data_for_obj(json_data)

    length = str(len(json_data_bytes))
    length = '0' * (8 - len(length)) + length

    length_data_bytes = get_binary_data_for_obj(length)

    all_data = length_data_bytes + json_data_bytes + binary_data
    return all_data


def get_strides_avg_and_std(numpoints, col):
    """
    stride data to get less numpoints.
    Calculate average and standard derivation for each stride
    :param col: column to calculate with
    :param numpoints: number of wanted points
    """

    strided, extra = get_strides_and_extra(numpoints, col)

    if strided is None or strided.size == 0:
        averages = col
        std = np.zeros(col.size)
    elif extra.size == 0:
        averages = np.nanmean(strided, axis=1)
        std = np.nanstd(strided, axis=1)
    else:
        averages = np.append(np.nanmean(strided, axis=1), np.nanmean(extra))
        std = np.append(np.nanstd(strided, axis=1), np.nanstd(extra))

    return averages, std


def get_strides_avg(numpoints, col):
    """
    stride data to get less numpoints.
    Calculate average for each stride
    :param col: column to calculate with
    :param numpoints: number of wanted points
    """

    strided, extra = get_strides_and_extra(numpoints, col)

    if strided is None or strided.size == 0:
        averages = col*1.0
    elif extra.size == 0:
        averages = np.nanmean(strided, axis=1)
    else:
        averages = np.append(np.nanmean(strided, axis=1), np.nanmean(extra))

    return averages


def get_strides_and_extra(numpoints, col):
    """
    stride data to get less numpoints.
    Calculate the strides and get the points left at the end as extra
    :param col: column to calculate with
    :param numpoints: number of wanted points
    """
    lx = col.size

    if lx <= numpoints:
        return None, None

    stride = int(lx / numpoints)

    points = numpoints * stride

    values_to_stride = col[:points]

    if hasattr(values_to_stride, 'values'):
        # pandas df or object behaving like it
        strided = values_to_stride.values.reshape((numpoints, stride))
    else:
        # numpy array or objects behaving like it
        strided = values_to_stride.reshape((numpoints, stride))

    extra = col[points:]

    return strided, extra


def get_max_value(array, default=0.0):
    value = np.nanmax(array)
    # array has only NaN values
    if np.isnan(value):
        return default
    else:
        return value


def get_min_value(array, default=0.0):
    value = np.nanmin(array)
    # array has only NaN values
    if np.isnan(value):
        return default
    else:
        return value
