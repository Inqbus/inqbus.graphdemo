STATIC_VIEWS = [
    'overview'
]

FILE_RELATED_VIEWS = [
    'diagramview'
]

DATABASE = 'sqlite:///test.db'

DEBUG_MODE = True

# Key for data-dictionary
SPECIAL_TABLES_ENTRY = "inqbus.graphdemo.tables"

UPLOAD_PATH = 'uploads/'
TABLE_URL_KEY = 'table'

# Contour Data set
#CONTOUR_DATA_SET ='/data/vms/ina/data/08/20150801_leipzig_CHM080079_000.h5'
CONTOUR_DATA_SET ='/home/volker/workspace/graph4/out.hdf5'

# Enable WebGL
WEBGL = True

# list of strings wich are inidcating a special JS-Object
SPECIAL_JS_TYPES = [
    'date_tick',  # for date axis
    'number_tick'  # for number_axis
]

# the default number of points which should be displayed if width and height of the plot is unknown
# None if all points should be displayed
MAX_NUMBERS_DEFAULT = 400
# Factor to correct number of maxpoints in Contourplots. E.g. Use 0.5 for
# using half of the points.
MAX_POINTS_CORRECTION = 1.0

# Remove duplicates before transferring data
REMOVE_DUPLICATES = True

# Debounce period in seconds
DEBOUNCE_CALLBACK_PERIOD = 0.3

FLASK_HOST = '0.0.0.0:5000'
BOKEH_HOST = '193.239.28.155:8020'

BOKEH_URL = 'http://' + BOKEH_HOST

# Contour_ranges
X_MAX_CONTOUR = 10.0
X_MIN_CONTOUR = 0.0
Y_MAX_CONTOUR = 10.0
Y_MIN_CONTOUR = 0.0

# display red lines with standard derivation
DISPLAY_STD = False
