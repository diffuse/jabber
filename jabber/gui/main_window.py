import glob
import logging
import os
from jabber.gui import MWBase, MWForm
from PyQt5.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)


class MainWindow(MWBase, MWForm):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self._connect_signals()
        self._img_fnames = list()

    def _connect_signals(self):
        """
        Connect signals to the appropriate slots
        """
        self.action_open.triggered.connect(self._get_input_files)

    def _get_input_files(self):
        """
        Get a list of image files with known
        extensions from user-chosen path
        """
        path = QFileDialog.getExistingDirectory(self, 'Select directory containing images to label')

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
