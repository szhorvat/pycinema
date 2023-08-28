from pycinema import Filter
from pycinema.theater.views.FilterView import FilterView

import numpy
from PySide6 import QtCore, QtWidgets, QtGui

class _ImageViewer(QtWidgets.QGraphicsView):

    def __init__(self):
        super().__init__()

        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        l = 10000
        self.setSceneRect(-l,-l,2*l,2*l)

        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

        self.items = []

    def removeImages(self):
        for item in self.items:
            self._scene.removeItem(item)
        self.items = []

    def addImage(self,image,x,y):
        item = QtWidgets.QGraphicsPixmapItem()

        rgba = image.channels['rgba']
        qimage = QtGui.QImage(
          rgba,
          rgba.shape[1], rgba.shape[0],
          rgba.shape[1] * 4,
          QtGui.QImage.Format_RGBA8888
        )
        item.setPixmap( QtGui.QPixmap(qimage) )
        item.setShapeMode(QtWidgets.QGraphicsPixmapItem.BoundingRectShape)
        item.setTransformationMode(QtCore.Qt.SmoothTransformation)

        item.setPos(x,y)

        self._scene.addItem(item)
        self.items.append(item)

    def fitInView(self):
        rect = QtCore.QRectF(self._scene.itemsBoundingRect())
        if rect.isNull():
            return

        self.resetTransform()
        super().fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        ZOOM_INCREMENT_RATIO = 0.1

        angle = event.angleDelta().y()
        factor = 1.0
        if angle > 0:
            factor += ZOOM_INCREMENT_RATIO
        else:
            factor -= ZOOM_INCREMENT_RATIO

        self.scale(factor, factor)

    def keyPressEvent(self,event):
        if event.key()==32:
            self.fitInView()

class ImageView(Filter, FilterView):

    def __init__(self):
        FilterView.__init__(
          self,
          filter=self,
          delete_filter_on_close = True
        )

        Filter.__init__(
          self,
          inputs={
            'images': []
          }
        )

    def generateWidgets(self):
        self.view = _ImageViewer()
        self.content.layout().addWidget(self.view,1)

    def _update(self):
        self.view.removeImages()

        max_w = 0
        max_h = 0
        images = self.inputs.images.get()
        for image in images:
          max_w = max(image.shape[0],max_w)
          max_h = max(image.shape[1],max_h)
        max_w += 5
        max_h += 5

        nRows = int(numpy.ceil(numpy.sqrt(len(images))))
        nCols = int(numpy.ceil(len(images)/nRows))

        i = 0
        for r in range(0,nRows):
          for c in range(0,nCols):
            if i<len(images):
              self.view.addImage(images[i],r*max_h,c*max_w)
              i+=1

        self.view.fitInView()
        return 1