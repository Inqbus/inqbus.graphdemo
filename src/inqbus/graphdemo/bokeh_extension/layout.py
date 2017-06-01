import math

from bokeh.core.properties import Instance, Float
from bokeh.core.enums import TextBaseline, Orientation, TextAlign

from bokeh.embed import components
from bokeh.layouts import column, row
from bokeh.models import LayoutDOM, Select, Plot, \
    ColumnDataSource, DataTable, \
    TableColumn, Range1d, ColorBar, BasicTicker, \
    LinearColorMapper, DateFormatter, DatetimeTickFormatter, MultiSelect
from bokeh.palettes import RdYlGn11
from bokeh.plotting import figure
from bokeh.resources import INLINE
from inqbus.graphdemo import constants
from inqbus.graphdemo.bokeh_extension.helpers import get_min_value, \
    get_max_value
from inqbus.graphdemo.bokeh_extension.helpers_xy import get_diagram_data, \
    get_plot_data_python
from inqbus.graphdemo.constants import UPLOAD_PATH, X_MIN_CONTOUR, \
    X_MAX_CONTOUR, Y_MIN_CONTOUR, Y_MAX_CONTOUR, DISPLAY_STD, X_AXIS_DATES, \
    USE_DATA_FILTER, OPTIONS_FOR_DATAFILTER, COLUMN_FOR_DATAFILTER
from inqbus.graphdemo.views.overview import get_files_by_path


class XYPlotJSLayout(LayoutDOM):
    """
    Testlayout using JS callbacks
    """

    __implementation__ = "coffeescripts/jslayout.coffee"
    __javascript__ = "http://underscorejs.org/underscore-min.js"

    table_select = Instance(Select)

    x_axis = Instance(Select)

    y_axis = Instance(Select)

    plot = Instance(Plot)

    data = Instance(ColumnDataSource)

    source = Instance(ColumnDataSource)

    table_plot = Instance(DataTable)

    data_filter = Instance(MultiSelect)

    def __init__(self, *args, **kwargs):
        """
        create all parts of the layout in their initialised way with default data.
        Changes will be handled by jslayout.coffee
        """
        super(XYPlotJSLayout, self).__init__(*args, **kwargs)

        self.initialize_select_boxes()

        x = []
        y = []

        self.source = ColumnDataSource(data=dict(
            x=x,
            y=y,
            y_below=y,
            y_above=y,
            index=x
        ))


        self.plot = figure(
            webgl=constants.WEBGL,
        )

        if X_AXIS_DATES:
            self.plot.xaxis.formatter=DatetimeTickFormatter(formats=dict(
                seconds=["%d.%m.%y %H:%M:%S"],
                minutes=["%d.%m.%y %H:%M:%S"],
                hourmin=["%d.%m.%y %H:%M:%S"],
                hours=["%d.%m.%y %Hh"],
                days=["%d.%m.%y"],
                months=["%b %y"],
                years=["%b %y"]))
            self.plot.xaxis.major_label_orientation=math.pi/2
            self.plot.xaxis.major_label_text_baseline=TextBaseline.top
            self.plot.xaxis.major_label_text_align=TextAlign.left

        if USE_DATA_FILTER:
            self.data_filter = MultiSelect(
                options = OPTIONS_FOR_DATAFILTER,
                value = OPTIONS_FOR_DATAFILTER,
                title = "Filter on %s" % COLUMN_FOR_DATAFILTER
            )
        else:
            self.data_filter = MultiSelect(
                options = [],
                value = [],
                title = 'Filtering is disabled'
            )

        self.plot.x_range = Range1d(start=0.0, end=10.0)
        self.plot.y_range = Range1d(start=0.0, end=10.0)

        self.plot.line(
            x='x',
            y='y',
            source=self.source,
            color='blue',
            line_width=2)

        if DISPLAY_STD:
            self.plot.line(
                x='x',
                y='y_below',
                source=self.source,
                color='red',
                line_width=1)
            self.plot.line(
                x='x',
                y='y_above',
                source=self.source,
                color='red',
                line_width=1)

        self.table_plot = DataTable(
            source=self.source,
            columns=[
                TableColumn(
                    field='x',
                    title='x average of slided data'),
                TableColumn(
                    field='y',
                    title='y average of slided data'),
                TableColumn(
                    field='y_above',
                    title='y + standard derivation'),
                TableColumn(
                    field='y_below',
                    title='y - standard derivation')])

    def get_colums(self, data, table):
        if table in data:
            columns = data[table]
        else:
            columns = []
        return columns

    def initialize_select_boxes(self):
        if self.data:
            data = dict(self.data.data)
        else:
            data = {}

        tables = self.get_tables(data)
        if not tables:
            tables = ['No table found']
        columns = self.get_colums(data, tables[0])
        if not columns:
            columns = ['No column found']

        self.table_select = Select(
            options=tables,
            title="Select a table",
            value=tables[0]
        )

        if 'date' in columns:
            x_value = 'date'
        elif 'time' in columns:
            x_value = 'time'
        else:
            x_value = columns[0]

        self.x_axis = Select(
            options=columns,
            title="Select a x axis",
            value=x_value
        )

        if len(columns) >= 2:
            self.y_axis = Select(
                options=columns,
                title="Select a y axis",
                value=columns[1]
            )
        else:
            self.y_axis = Select(
                options=columns,
                title="Select a y axis",
                value=columns[0]
            )

    def get_tables(self, data):
        return list(data.keys())

    def render_components(self):

        layout = column(self.table_select,
                        self.x_axis,
                        self.y_axis,
                        self.data_filter,
                        self,
                        row(self.plot,
                            self.table_plot))

        layout_script, div = components(layout)

        script = ''

        # Work around to use custom model
        for x in INLINE.js_raw:
            if "XYPlotJSLayout" in x:
                script += ('\n<script type="text/javascript">%s</script>\n' % x)

        script += layout_script

        return script, div


class XYPlotPythonLayout(XYPlotJSLayout):
    """
    Testlayout using Python-callbacks and bokeh-server
    """

    __implementation__ = 'coffeescripts/xyplotpythonlayout.coffee'

    file_select = Instance(Select)

    def __init__(self, *args, **kwargs):
        """
        Create all parts of the layout in their initialised way with default data.
        Register handler for python callbacks
        """
        super(XYPlotPythonLayout, self).__init__(*args, **kwargs)

        self.change_data_source_ignore_range(None, None, None)

        self.plot.y_range.on_change('start', self.change_data_source_in_range)
        self.plot.y_range.on_change('end', self.change_data_source_in_range)
        self.plot.x_range.on_change('start', self.change_data_source_in_range)
        self.plot.x_range.on_change('end', self.change_data_source_in_range)

        self.x_axis.on_change('value', self.change_data_source_ignore_range)
        self.y_axis.on_change('value', self.change_data_source_ignore_range)

        self.table_select.on_change('value', self.change_columns)

        self.file_select.on_change('value', self.change_tables)

    def initialize_select_boxes(self):
        """
        Initial selectboxes
        :return:
        """
        files = get_files_by_path(UPLOAD_PATH)
        if not files:
            files = ['No file found']

        self.file_select = Select(
            options=files,
            title="Select a file",
            value=files[0]
        )

        self.data = ColumnDataSource()

        self.data.data = get_diagram_data(UPLOAD_PATH, files[0])

        super(XYPlotPythonLayout, self).initialize_select_boxes()

    def change_tables(self, attrname, old, new):
        """
        a different file is selected and other tables are available
        """
        self.data.data = get_diagram_data(UPLOAD_PATH, self.file_select.value)

        tables = self.get_tables(self.data.data)
        if not tables:
            tables = ['No table found']

        self.table_select.options = tables
        self.table_select.value = tables[0]

    def change_columns(self, attrname, old, new):
        """
        a different table is selected and other columns are available
        """
        data = dict(self.data.data)
        table = self.table_select.value

        columns = self.get_colums(data, table)

        if len(columns) == 0:
            columns = ['No column found']

        self.x_axis.options = columns
        self.y_axis.options = columns


        self.x_axis.value = columns[0]
        if len(columns) >= 2:
            self.y_axis.value = columns[1]
        else:
            self.y_axis.value = columns[0]

    # @Debounce(period=DEBOUNCE_CALLBACK_PERIOD)
    def change_data_source_in_range(self, attrname, old, new):
        """
        deals with data generation after zooming
        """
        data = self.get_plot_data(ignore_ranges=False)

        self.source.data = dict(
            x=data['source.data.x'],
            y=data['source.data.y'],
            index=data['source.data.index'],
            y_above=data['source.data.y_above'],
            y_below=data['source.data.y_below']
        )

    # @Debounce(period=DEBOUNCE_CALLBACK_PERIOD)
    def change_data_source_ignore_range(self, attrname, old, new):
        """
        deals with data generation after selecting different columns
        """
        data = self.get_plot_data(ignore_ranges=True)

        self.plot.x_range.start = data['plot.x_range.start']
        self.plot.x_range.end = data['plot.x_range.end']
        self.plot.y_range.start = data['plot.y_range.start']
        self.plot.y_range.end = data['plot.y_range.end']

        self.source.data = dict(
            x=data['source.data.x'],
            y=data['source.data.y'],
            index=data['source.data.index'],
            y_above=data['source.data.y_above'],
            y_below=data['source.data.y_below']
        )

    def get_plot_data(self, ignore_ranges=True):
        """
        Calculating data
        :param ignore_ranges: True if complete data should be used, false if min and max depends on current ranges
        :return: dictionary with data for redraw
           'source.data.x': numpy array, floats
           'source.data.y': numpy array, floats
           'source.data.index': numpy array, floats
           'source.data.y_above': numpy array, floats
           'source.data.y_below': numpy array, floats
           'plot.x_range.start': float
           'plot.x_range.end': float
           'plot.y_range.start': float
           'plot.y_range.end': float

        """
        upload_path = UPLOAD_PATH
        filename = self.file_select.value
        tablepath = self.table_select.value
        x_col = self.x_axis.value
        y_col = self.y_axis.value

        if ignore_ranges:
            xmin = None
            xmax = None
            ymin = None
            ymax = None
        else:
            xmin = self.plot.x_range.start
            xmax = self.plot.x_range.end
            ymin = self.plot.y_range.start
            ymax = self.plot.y_range.end

        data = get_plot_data_python(
            upload_path,
            filename,
            tablepath,
            x_col=x_col,
            y_col=y_col,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            plotwidth=self.plot.width,
            plotheight=self.plot.height)

        return data

    def render_components(self):

        layout = column(self.file_select,
                        self.table_select,
                        self.x_axis,
                        self.y_axis,
                        row(self.plot,
                            self.table_plot))

        return layout


class ContourPlotLayout(LayoutDOM):

    __implementation__ = 'coffeescripts/jslayout.coffee'
    __javascript__ = "http://underscorejs.org/underscore-min.js"

    plot = Instance(Plot)
    data = Instance(ColumnDataSource)

    x_min = Float()
    x_max = Float()
    y_min = Float()
    y_max = Float()

    color_mapper = Instance(LinearColorMapper)

    color_bar = Instance(ColorBar)

    def __init__(self, *args, **kwargs):
        """
        Create all parts of the layout in their initialised way with default data.
        Register handler for python callbacks
        """
        super(ContourPlotLayout, self).__init__(*args, **kwargs)

        data = self.data.data

        image_data = data['image'][0]

        flat_image_data = image_data.flatten()

        min_data = get_min_value(flat_image_data)
        max_data = get_max_value(flat_image_data)

        self.color_mapper = LinearColorMapper(
            palette=RdYlGn11, low=min_data, high=max_data)

        if 'x_min' in data:
            x_min = data['x_min']
        else:
            x_min = self.x_min
        if 'x_max' in data:
            x_max = data['x_max']
        else:
            x_max = self.x_max
        if 'y_min' in data:
            y_min = data['y_min']
        else:
            y_min = self.y_min
        if 'y_max' in data:
            y_max = data['y_max']
        else:
            y_max = self.y_max

#        self.data.X0 = x_min
#        self.data.Y0 = y_min
#        self.data.DX= x_max-x_min
#        self.data.DY= y_max-y_min

        self.plot = figure(plot_width=600,
                           plot_height=400,
                           x_range= [x_min, x_max],
                           y_range = [y_min, y_max],
#                           x_range=[X_MIN_CONTOUR, X_MAX_CONTOUR],
#                           y_range=[Y_MIN_CONTOUR, Y_MAX_CONTOUR],
                           min_border_right=10)

#        self.plot.image(image='image',
#                        x='X0',
#                        y='Y0',
#                        dw='DX',
#                        dh='DY',
#                        color_mapper=self.color_mapper,
#                        source=self.data)

        self.plot.image(image='image',
                        x=x_min,
                        y=y_min,
                        dw=x_max-x_min,
                        dh=y_max-y_min,
                        color_mapper=self.color_mapper,
                        source=self.data)

        self.color_bar = ColorBar(
            color_mapper=self.color_mapper,
            ticker=BasicTicker(desired_num_ticks=10),
            label_standoff=12,
            border_line_color=None,
            location=(0, 0))

        self.plot.add_layout(self.color_bar, 'left')

    def render_components(self):

        layout = column(self.plot, self)

        layout_script, div = components(layout)

        script = ''

        # Work around to use custom model
        for x in INLINE.js_raw:
            if "ContourPlotLayout" in x:
                script += ('\n<script type="text/javascript">%s</script>\n' % x)

        script += layout_script

        return script, div
