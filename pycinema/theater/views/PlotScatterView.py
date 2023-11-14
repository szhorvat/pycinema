from pycinema import Filter

from PySide6 import QtCore, QtWidgets, QtGui

from .FilterView import FilterView

import numpy as np
import pyqtgraph as pg

class PlotScatterView(Filter, FilterView):

    def __init__(self):
        FilterView.__init__(
          self,
          filter=self,
          delete_filter_on_close = True
        )

        Filter.__init__(
          self,
          inputs={
            'title'     : 'Plot Title',
            'background': 'white',
            'plotitem'  : 'none'
          }
        )

    def generateWidgets(self):
        self.plot = pg.PlotWidget() 
        self.content.layout().addWidget(self.plot)

    def _update(self):
        # clear on update
        self.plot.clear()

        # get plot items
        # for now, there is only one item, but there will be a list in the future
        item = self.inputs.plotitem.get()

        # pen
        pencolor = item['pen']['color']
        if pencolor == 'default':
            pencolor = 'black'
        itempen = pg.mkPen(width=item['pen']['width'],color=pencolor)

        # brush
        brushcolor = item['brush']['color']
        if brushcolor == 'default':
            brushcolor = 'black'
        itembrush = pg.mkBrush(color=brushcolor)

        # graph item
        plotItem = pg.ScatterPlotItem(x=item['x']['data'], y=item['y']['data'], pen=itempen, brush=itembrush, symbol=item['symbol'], size=item['size'])

        # set up the plot
        self.plot.setBackground(self.inputs.background.get())
        self.plot.setTitle(self.inputs.title.get())
        self.plot.setLabel("left", item['y']['label']) 
        self.plot.setLabel("bottom", item['x']['label']) 
        self.plot.addItem(plotItem)

        return 1
