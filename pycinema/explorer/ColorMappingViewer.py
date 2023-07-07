from pycinema import Filter

from .FilterView import ViewFilter

from PySide6 import QtCore, QtWidgets

import numpy
import matplotlib.cm as cm

class ColorMappingViewer(ViewFilter):

    def __init__(self, view):

        self.widgets_ = {}
        self.widgets = QtWidgets.QFrame()
        self.widgets.setLayout(QtWidgets.QGridLayout())
        view.content.layout().addWidget(self.widgets)
        view.content.layout().addWidget(QtWidgets.QLabel(""),1)

        super().__init__(
          inputs={
            'images': [],
            'channel': 'rgba',
            'map': 'plasma',
            'range': (0,1),
            'nan': (1,1,1,1),
            'composition_id': -1
          },
          outputs={
            'images': []
          }
        )

    def update_channels(self,images):
        channels = set({})
        for i in images:
            for c in i.channels:
                channels.add(c)
        w = self.widgets_['channel']
        if set(w.channels) == channels:
            return

        if len(w.channels)>0:
            w.old_v = w.currentText()

        new_channels = list(channels)
        new_channels.sort()

        w.clear()
        for c in new_channels:
            w.addItem(c)
        w.channels = new_channels

        if w.old_v in new_channels:
            w.setCurrentText(w.old_v)
        elif 'rgba' in new_channels:
            w.setCurrentText('rgba')
        elif 'depth' in new_channels:
            w.setCurrentText('depth')
        else:
            for c in new_channels:
                w.setCurrentText(c)
                break

    def generate_widgets(self, images):
        gridL = self.widgets.layout()

        row = 0

        w = QtWidgets.QComboBox()
        self.widgets_['channel'] = w
        w.channels = []
        w.old_v = self.inputs.channel.get()
        gridL.addWidget(QtWidgets.QLabel("Channel"),row,0)
        gridL.addWidget(w,row,1)
        self.update_channels(images)
        w.currentTextChanged.connect( lambda v: self.inputs.channel.set(v) )
        row += 1

        w = QtWidgets.QComboBox()
        self.widgets_['map'] = w
        gridL.addWidget(QtWidgets.QLabel("Color Map"),row,0)
        gridL.addWidget(w,row,1)
        w.addItems([
            'plasma',

            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',

            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
            'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',

            'fixed'
        ])
        w.setCurrentText(self.inputs.map.get())
        w.currentTextChanged.connect( lambda v: self.inputs.map.set(v) )
        row += 1

        # RANGE
        f = QtWidgets.QFrame()
        f.setLayout( QtWidgets.QHBoxLayout())
        gridL.addWidget(QtWidgets.QLabel("Range"),row,0)
        gridL.addWidget(f,row,1)

        w0 = QtWidgets.QLineEdit()
        w1 = QtWidgets.QLineEdit()
        self.widgets_['range'] = [w0,w1]
        w0.setText(str(self.inputs.range.get()[0]))
        w1.setText(str(self.inputs.range.get()[1]))
        l = lambda v: self.inputs.range.set( (float(w0.text()), float(w1.text())) )
        w0.textEdited.connect(l)
        w1.textEdited.connect(l)
        f.layout().addWidget(w0)
        f.layout().addWidget(w1)
        row+=1

        # NAN COLOR
        def select_color():
            clrpick = QtWidgets.QColorDialog()
            clrpick.setOption(QtWidgets.QColorDialog.DontUseNativeDialog)
            color = clrpick.getColor()
            color = (color.redF(),color.greenF(),color.blueF(),color.alphaF())
            self.widgets_['nan'].setText(str(color))
            self.inputs.nan.set(color)

        w = QtWidgets.QPushButton()
        w.setText(str(self.inputs.nan.get()))
        w.clicked.connect(select_color)
        self.widgets_['nan'] = w
        gridL.addWidget(QtWidgets.QLabel("NAN Color"),row,0)
        gridL.addWidget(w,row,1)
        row += 1


    def _update(self):
        i_images = self.inputs.images.get()
        if self.widgets_ == {}:
            self.generate_widgets(i_images)
        else:
            self.update_channels(i_images)

        i_channel = self.inputs.channel.get()
        i_map = self.inputs.map.get()
        i_nan = self.inputs.nan.get()
        i_composition_id = self.inputs.composition_id.get()

        nanColor = numpy.array(tuple([f * 255 for f in i_nan]),dtype=numpy.uint8)

        cmap = cm.get_cmap( i_map )
        cmap.set_bad(color=i_nan )
        i_range = self.inputs.range.get()
        d = i_range[1]-i_range[0]

        o_images = []
        for i_image in i_images:
            if not i_channel in i_image.channels or i_channel=='rgba':
                o_images.append(i_image)
                continue

            normalized = (i_image.channels[ i_channel ]-i_range[0])/d
            if i_channel == 'depth':
                normalized[i_image.channels[i_channel]==1] = numpy.nan

            o_image = i_image.copy()
            if i_composition_id>=0 and 'composition_mask' in o_image.channels:
                rgba = None
                if 'rgba' not in o_image.channels:
                    rgba = numpy.full((o_image.shape[0],o_image.shape[1],4), nanColor, dtype=numpy.uint8)
                    o_image.channels['rgba'] = rgba
                else:
                    rgba = o_image.channels['rgba']

                mask = o_image.channels['composition_mask']==i_composition_id
                rgba[mask] = cmap(normalized[mask], bytes=True)
            else:
                o_image.channels["rgba"] = cmap(normalized, bytes=True)

            o_images.append(o_image)

        self.outputs.images.set(o_images)

        return 1