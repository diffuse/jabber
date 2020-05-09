import logging
from jabber import gui as gui
from PyQt5 import QtCore, QtGui

logger = logging.getLogger(__name__)


class ImageWidget(gui.ImgBase, gui.ImgForm):
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


class ImageListWidget(gui.ImgListBase, gui.ImgListForm):
    fname_selected = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.list.setSortingEnabled(True)
        self.list.itemClicked.connect(self._fname_selected)

    def add_items(self, items):
        """
        Add list of items to list widget

        :param items: The list of items to add
        """
        self.list.addItems(items)

    def set_idx(self, idx):
        """
        Highlight the fname at this index

        :param idx: The index/row of the fname to enable highlighting on
        """
        self.list.setCurrentRow(idx)

    def _fname_selected(self, fname):
        """
        Signal for a filename being selected
        """
        self.fname_selected.emit(fname.text())


class ClassListWidget(gui.ClassListBase, gui.ClassListForm):
    item_deleted = QtCore.pyqtSignal(str)
    item_double_clicked = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.list.setSortingEnabled(True)
        self.list.itemDoubleClicked.connect(lambda item: self.item_double_clicked.emit(item.text()))

    def add_items(self, items):
        """
        Add list of items to list widget

        :param items: The list of items to add
        """
        self.list.addItems(items)

    def clear(self):
        """
        Clear the list
        """
        self.list.clear()

    def keyPressEvent(self, e):
        """
        Perform actions based on key press

        :param e: The event
        """
        key = e.key()

        if key == QtCore.Qt.Key_Delete:
            for item in self.list.selectedItems():
                self.list.takeItem(self.list.row(item))
                self.item_deleted.emit(item.text())

