import logging
from jabber.gui import ImgBase, ImgForm
from PyQt5 import QtCore, QtGui

logger = logging.getLogger(__name__)


class ImageWidget(ImgBase, ImgForm):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self._current_fname = ''

    def load_img(self, fname):
        """
        Load an image from filename into this label

        :param fname: The filename of the image to load
        """
        # try load the image
        p = QtGui.QPixmap(fname)

        if p.isNull():
            logger.warning(f'invalid image filename: {fname}')
            return

        # scale the pixmap
        p = p.scaled(self.label.size(), aspectRatioMode=QtCore.Qt.KeepAspectRatio)

        # set the pixmap
        self.label.setPixmap(p)
        self._current_fname = fname

    def resizeEvent(self, e):
        """
        Reload the current image when the widget
        is resized to fill the label

        :param e: The event
        """
        if self._current_fname:
            self.load_img(self._current_fname)
