'use strict'
# These are similar to python imports. BokehJS vendors its own versions
# of Underscore and JQuery. They are available as show here.
import * as $ from "jquery"

# The "core/properties" module has all the property types
import * as p from "core/properties"

# We will subclass in JavaScript from the same class that was subclassed
# from in Python
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

# base class to provide encoding functions for converting binary data
export class BaseJSView extends LayoutDOMView

  initialize: (options) ->
    super(options)

    return

  array_to_string: (array, encoding='utf-8') ->
    dataView = new DataView(array)
    decoder = new TextDecoder(encoding)
    decodedString = decoder.decode(dataView)
    return decodedString

  string_to_integer: (string) ->
    int = parseInt(string)
    return int

  string_to_float: (string) ->
    float = parseFloat(string)
    return float

  string_to_json: (string) ->
    json = JSON.parse(string)
    return json

  array_to_float: (array) ->
    string = @array_to_string(array, 'utf-8')
    float = parseFloat(string)
    return float

  array_to_int: (array) ->
    string = @array_to_string(array, 'utf-8')
    int = parseInt(string)
    return int

  array_to_floatlist: (array) ->
    list = new Float64Array(array)
    return list

  array_to_shape: (array) ->
    encoded_string = @array_to_string(array, 'utf-8')
    number_strings = encoded_string.split(';')
    i = 0
    len = number_strings.length
    shape = []
    while i < len
      number_string = number_strings[i]
      shape[i] = @string_to_float(number_string)
      i++
    return shape


  set_attribute: (value, attribute) ->
    path = attribute.split('.')
    attribute_name = path[path.length-1]
    path = path.slice(0,-1)
    object = @model
    object = object[path_element] for path_element in path
    if (typeof object.setv == 'function')
      object.setv(attribute_name, value, {silent: true})
    else
      object[attribute_name] = value
    return

  read_attribute: (data, type, attribute) ->
    value = null
    if type == 'float'
      value = @array_to_float(data)
    else if type == 'string'
      value = @array_to_string(data, 'utf-8')
    else if type == 'floatlist'
      value = @array_to_floatlist(data)
    else if type == 'contourdata'
      data_value = @array_to_floatlist(data)
      value = [data_value]
    else if type == 'contourattr'
      value = [@array_to_float(data)]
    else if type == 'contourshape'
      value = [@array_to_shape(data)]
    if value
        @set_attribute(value, attribute)
    return

  read_attributes: (data_array, json) ->
    keys = Object.keys(json)
    l = 0
    number_of_keys = keys.length
    while l < number_of_keys
      key = keys[l]
      meta_data = json[key]
      current_offset = @string_to_integer(meta_data['offset'])
      data_length = @string_to_integer(meta_data['length'])
      data = data_array.slice(current_offset, current_offset+data_length)
      type = meta_data['type']
      attribute = meta_data['attribute']
      @read_attribute(data, type, attribute)
      l++
    return



export class ContourPlotLayoutView extends BaseJSView

  initialize: (options) ->
    super(options)

    # Set Backbone listener so that when the Bokeh parts have a change
    # event, we can process the new data
    @listenTo(@model.plot.x_range, 'change:start', @update_plot_with_ranges)
    @listenTo(@model.plot.x_range, 'change:end', @update_plot_with_ranges)
    @listenTo(@model.plot.y_range, 'change:start', @update_plot_with_ranges)
    @listenTo(@model.plot.y_range, 'change:end', @update_plot_with_ranges)

    @read_data(ignore_range=true)

    return



  read_data: (ignore_range=true) ->

    if ignore_range
      x_range_min = null
      x_range_max = null
      y_range_min = null
      y_range_max = null

    else
      x_range_min = @model.plot.x_range.start
      x_range_max = @model.plot.x_range.end
      y_range_min = @model.plot.y_range.start
      y_range_max = @model.plot.y_range.end

    url = window.location.href + '/data'
    data = {
        'plot_width': @model.plot.width,
        'plot_height': @model.plot.height,
        'x_min': x_range_min,
        'x_max': x_range_max,
        'y_min': y_range_min,
        'y_max': y_range_max,
    }

    return jQuery.ajax
      type: 'POST'
      url: url
      data: data
      dataType: 'binary'
      responseType:'arraybuffer'
      success: $.proxy((data_from_server, errorCode, xhr) ->
          length_array = data_from_server.slice(0,8)
          length_string = @array_to_string(length_array, 'utf-8')
          length_int = @string_to_integer(length_string)

          meta_data_end = 8+length_int

          json_array = data_from_server.slice(8, meta_data_end)

          json_string = @array_to_string(json_array, 'utf-8')

          json = @string_to_json(json_string)

          @read_attributes(data_from_server.slice(meta_data_end), json)

          @model.data.trigger 'change'
          return
        ,this)
      error: ->
        alert 'Oh no, something went wrong. Search for an error ' + 'message in Flask log and browser developer tools.'
        return


  update_plot: _.debounce(() ->
    @read_data(ignore_range=true)
    return
  , 300, false)

  update_plot_with_ranges: _.debounce(() ->
    @read_data(ignore_range=false)
    return
  , 300, false)


export class ContourPlotLayout extends LayoutDOM

  # If there is an associated view, this is boilerplate.
  default_view: ContourPlotLayoutView

  # The ``type`` class attribute should generally match exactly the name
  # of the corresponding Python class.
  type: "ContourPlotLayout"

  # The @define block adds corresponding "properties" to the JS model. These
  # should basically line up 1-1 with the Python model class. Most property
  # types have counterparts, e.g. bokeh.core.properties.String will be
  # p.String in the JS implementation. Where the JS type system is not yet
  # as rich, you can use p.Any as a "wildcard" property type.
  @define {
    plot: [ p.Any    ]

    data: [p.Any]

    color_mapper: [p.Any]

    color_bar: [p.Any]
  }


export class XYPlotJSLayoutView extends BaseJSView

  initialize: (options) ->
    super(options)


    # Set Backbone listener so that when the Bokeh parts have a change
    # event, we can process the new data
    @listenTo(@model.table_select, 'change', @update_axis)
    @listenTo(@model.x_axis, 'change', @update_plot)
    @listenTo(@model.y_axis, 'change', @update_plot)
    @listenTo(@model.plot.x_range, 'change:start', @update_plot_with_ranges)
    @listenTo(@model.plot.x_range, 'change:end', @update_plot_with_ranges)
    @listenTo(@model.plot.y_range, 'change:start', @update_plot_with_ranges)
    @listenTo(@model.plot.y_range, 'change:end', @update_plot_with_ranges)

    @read_data(ignore_range=true)

    return

  update_axis: () ->
    data = @model.data.data
    table = @model.table_select.value

    # get all columns in data
    columns = data[table]

    # if there is a empty table with no columns specified return default
    if columns.length == 0
        columns = ['No column found']

    # set new values to axis
    @model.x_axis.options = columns
    @model.y_axis.options = columns
    @model.x_axis.value = columns[0]
    @model.y_axis.value = columns[0]

    @update_plot()


  update_initials: () ->
    @model.plot.x_range._initial_end = @model.plot.x_range.end
    @model.plot.x_range._initial_start = @model.plot.x_range.start
    @model.plot.y_range._initial_end = @model.plot.y_range.end
    @model.plot.y_range._initial_start = @model.plot.y_range.start


  read_data: (ignore_range=true) ->

    if ignore_range
      x_range_min = null
      x_range_max = null
      y_range_min = null
      y_range_max = null

    else
      x_range_min = @model.plot.x_range.start
      x_range_max = @model.plot.x_range.end
      y_range_min = @model.plot.y_range.start
      y_range_max = @model.plot.y_range.end

    url = window.location.href + '/data'
    data = {
        'table': @model.table_select.value,
        'plot_width': @model.plot.width,
        'plot_height': @model.plot.height,
        'x_min': x_range_min,
        'x_max': x_range_max,
        'y_min': y_range_min,
        'y_max': y_range_max,
        'x_column': @model.x_axis.value,
        'y_column': @model.y_axis.value,
    }

    return jQuery.ajax
      type: 'POST'
      url: url
      data: data
      dataType: 'binary'
      responseType:'arraybuffer'
      success: $.proxy((data_from_server, errorCode, xhr) ->
          length_array = data_from_server.slice(0,8)
          length_string = @array_to_string(length_array, 'utf-8')
          length_int = @string_to_integer(length_string)

          meta_data_end = 8+length_int

          json_array = data_from_server.slice(8, meta_data_end)

          json_string = @array_to_string(json_array, 'utf-8')

          json = @string_to_json(json_string)

          @read_attributes(data_from_server.slice(meta_data_end), json)
          
          if ignore_range
            @update_initials()


          @model.source.trigger 'change'

          return
        ,this)
      error: ->
        alert 'Oh no, something went wrong. Search for an error ' + 'message in Flask log and browser developer tools.'
        return


  update_plot: _.debounce(() ->
    @read_data(ignore_range=true)
    return
  , 300, false)

  update_plot_with_ranges: _.debounce(() ->
    @read_data(ignore_range=false)
    return
  , 300, false)


export class XYPlotJSLayout extends LayoutDOM

  # If there is an associated view, this is boilerplate.
  default_view: XYPlotJSLayoutView

  # The ``type`` class attribute should generally match exactly the name
  # of the corresponding Python class.
  type: "XYPlotJSLayout"

  # The @define block adds corresponding "properties" to the JS model. These
  # should basically line up 1-1 with the Python model class. Most property
  # types have counterparts, e.g. bokeh.core.properties.String will be
  # p.String in the JS implementation. Where the JS type system is not yet
  # as rich, you can use p.Any as a "wildcard" property type.
  @define {
    table_select: [ p.Any    ]

    x_axis: [ p.Any    ]
    
    y_axis: [ p.Any    ]
    
    plot: [ p.Any    ]

    data: [p.Any]

    source: [p.Any]

    table_plot: [p.Any]
  }