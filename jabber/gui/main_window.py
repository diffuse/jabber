from jabber.gui import MWBase, MWForm
from PyQt5.QtWidgets import QFileDialog


class MainWindow(MWBase, MWForm):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self._connect_signals()

    def _connect_signals(self):
        """
        Connect signals to the appropriate slots
        """
        self.action_open.triggered.connect(self._get_input_dir)

    def _get_input_dir(self):
        """
        Get the input directory for images
        """
        self._input_dir = QFileDialog.getExistingDirectory(self, 'Select directory containing images to label')
