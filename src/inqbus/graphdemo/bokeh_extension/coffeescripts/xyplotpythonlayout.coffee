'use strict'
# These are similar to python imports. BokehJS vendors its own versions
# of Underscore and JQuery. They are available as show here.
import * as $ from "jquery"

# The "core/properties" module has all the property types
import * as p from "core/properties"

# We will subclass in JavaScript from the same class that was subclassed
# from in Python
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

# This model will actually need to render things, so we must provide
# view. The LayoutDOM model has a view already, so we will start with that
export class XYPlotPythonLayoutView extends LayoutDOMView

  initialize: (options) ->
    super(options)

    return

export class XYPlotPythonLayout extends LayoutDOM

  # If there is an associated view, this is boilerplate.
  default_view: XYPlotPythonLayoutView

  # The ``type`` class attribute should generally match exactly the name
  # of the corresponding Python class.
  type: "XYPlotPythonLayout"

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

    file_select: [p.Any]
  }