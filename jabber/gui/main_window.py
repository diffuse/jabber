import glob
import logging
import os
from jabber.gui import MWBase, MWForm
from PyQt5 import QtCore, QtWidgets

logger = logging.getLogger(__name__)


class MainWindow(MWBase, MWForm):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self._connect_signals()
        self._img_fnames = list()
        self._img_idx = -1

    def _connect_signals(self):
        """
        Connect signals to the appropriate slots
        """
        self.action_open.triggered.connect(self._get_input_files)
        self.fname_list.fname_selected.connect(self._jump_to_img)

    def _get_input_files(self):
        """
        Get a list of image files with known
        extensions from user-chosen path
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory containing images to label')

        # check the path
        if not path:
            logger.warning('no path provided')
            return

        # enforce trailing slash
        path = os.path.join(path, '')

        # search for known image types
        for ext in ['jpg', 'jpeg', 'png']:
            ext = ''.join([f'[{c.lower()}{c.upper()}]' for c in ext])
            self._img_fnames.extend(glob.glob(f'{path}*.{ext}'))

        # sort the file names
        self._img_fnames = sorted(self._img_fnames)
        self.fname_list.add_items(self._img_fnames)
        self._next_img()

    def _next_img(self):
        """
        Load the next image
        """
        try:
            self._img_idx += 1

            # wrap around if necessary
            if self._img_idx >= len(self._img_fnames):
                self._img_idx = 0

            self.image.load_img(self._img_fnames[self._img_idx])
            self.fname_list.set_idx(self._img_idx)
        except IndexError:
            logger.warning('no images to display')

    def _prev_img(self):
        """
        Load the previous image
        """
        try:
            self._img_idx -= 1

            # wrap around if necessary
            if self._img_idx < 0:
                self._img_idx = len(self._img_fnames) - 1

            self.image.load_img(self._img_fnames[self._img_idx])
            self.fname_list.set_idx(self._img_idx)
        except IndexError:
            logger.warning('no images to display')

    def _jump_to_img(self, fname):
        """
        Load/jump to the file fname

        :param fname: The name of the file to jump to
        """
        self._img_idx = self._img_fnames.index(fname)
        self.image.load_img(fname)

    def keyPressEvent(self, e):
        """
        Move to the next or previous image
        based on key presses

        :param e: The key press event
        """
        if e.key() == QtCore.Qt.Key_Right:
            self._next_img()
        elif e.key() == QtCore.Qt.Key_Left:
            self._prev_img()
