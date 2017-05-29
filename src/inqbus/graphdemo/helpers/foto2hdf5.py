import tables as tb
import numpy as np
from PIL import Image

def image2pixelarray(filepath):
    """
    Parameters
    ----------
    filepath : str
        Path to an image file

    Returns
    -------
    list
        A list of lists which make it simple to access the greyscale value by
        im[y][x]
    """
    im = Image.open(filepath).convert('L')
    (width, height) = im.size
    greyscale_map = list(im.getdata())
    greyscale_map = np.array(greyscale_map)
    greyscale_map = greyscale_map.reshape((height, width))
    return greyscale_map


array = image2pixelarray('/picture_store/bilder/2017/2017_04_23_tulpen_beamen/IMG_7196.JPG')

hdf5_file = tb.open_file('out.hdf5','w')
group = hdf5_file.create_group("/", 'raw_signal', 'Detector information')
hdf5_file.create_array(group, 'beta_raw', array)

hdf5_file.create_array(group, 'time', np.arange(array.shape[0]))
hdf5_file.create_array(group, 'height', np.arange(array.shape[1]))


hdf5_file.close()