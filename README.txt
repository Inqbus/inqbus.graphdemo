Inqbus.graphdemo
================

This package shows an example of how to use bokeh with large datasets.

It uses flask as webframework and Hdf5-files to provide data.

Installation and requirements
-----------------------------

This package is written for Python3.

For installing all requirements just run the setup.py. Make sure you have installed
global requirements first. You can find them in docs/requirements.

.. code:: python3 setup.py install

Then you can start the flask process by running the main.py located in inqbus.graphdemo via python.

.. code:: python3 main.py

Examples included
-----------------

The package includes 3 examples located in inqbus.graphdemo.bokeh_extension.layout.

The first example is XYPlotJSLayout used for xy-plots based on JS and binary-transmitted data.
The second one is XYPlotPythonLayout displaying the same plots. This can be used
for performance comparison.

The last example is ContourPlotLayout for 3D-Data. It is also based on binary-transmitted data.

Features included
-----------------

The main features are:
* optimized performance due to reduced data:
    * First, data is filtered out of the given axis areas. Subsequently, the data is averaged so that only a reasonable number is transmitted.
    * For reducing the data fast libaries like numpy, pandas and dask are used.
* data on request:
    * Instead of transmitting all data simultaneously, the data required data is calculated and transferred when the selection parameters or zoom operations have been changed.
* easy-to-use
    * The layouts can be equipped with the required initial data via simple builder functions.
    * These functions are located in inqbus.graphdemo.bokeh_extension.builder
