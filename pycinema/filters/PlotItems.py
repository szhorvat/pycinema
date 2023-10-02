from pycinema import Filter

import PIL
import numpy

#
# PlotItems
#
# To be paired with a plot view
# Question: should this be a filter, or some new thing?
# Doesn't seem to fit the design of a view or filter
#
class PlotItems(Filter):

    def __init__(self):
        super().__init__(
          inputs={
            'x'     : 'none',
            'y'     : 'none',
            'line'  : 'default',
            'color' : 'default',
            'width' : 1.0 
          },
          outputs={
            'items' : 'none'
          }
        )

    def _update(self):
        outs = [[[  self.inputs.x.get(), self.inputs.y.get()], 
                    self.inputs.line.get(), self.inputs.color.get(), self.inputs.width.get()]]
        self.outputs.items.set(outs)

        return 1
