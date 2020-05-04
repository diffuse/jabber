import glob
import logging
import os
from jabber.gui import MWBase, MWForm
from jabber.label import Labeler
from jabber.voice import Listener
from PyQt5 import QtCore, QtWidgets

logger = logging.getLogger(__name__)


class MainWindow(MWBase, MWForm):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # images
        self._img_fnames = list()
        self._img_idx = -1

        # labeling
        self._labeler = None
        self._listener = Listener()

        # signals
        self._connect_signals()

        # configure event handling
        self.installEventFilter(self)
        self.fname_list.setFocusPolicy(QtCore.Qt.StrongFocus)

    def _connect_signals(self):
        """
        Connect signals to the appropriate slots
        """
        self.action_open.triggered.connect(self._get_input_files)
        self.action_set_labels_file.triggered.connect(self._get_labels_fname)
        self.fname_list.fname_selected.connect(self._jump_to_img)
        self.mic_control.ambience_btn.clicked.connect(lambda: self._listener.adjust_for_ambient_noise())

    def _get_input_files(self):
        """
        Get a list of image files with known
        extensions from user-chosen path
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Select directory containing images to label',
            options=QtWidgets.QFileDialog.DontUseNativeDialog)

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

    def _get_labels_fname(self):
        """
        Get a filename to save labels with
        """
        labels_fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Select filename to save labels to',
            filter='json(*.json)',
            options=QtWidgets.QFileDialog.DontConfirmOverwrite | QtWidgets.QFileDialog.DontUseNativeDialog)

        if not labels_fname:
            logger.warning('no labels filename provided')
            return

        self._labeler = Labeler(f'{labels_fname}.json')

    def _refresh_classes(self):
        """
        Make sure the class list is current
        """
        self.classes.clear()

        if self._labeler:
            self.classes.add_items(self._labeler.get_classes())

    def _load(self):
        """
        Load image at self._img_idx and handle
        related state changes
        """
        # clear current labels and refresh class list
        self.current_labels.clear()
        self._refresh_classes()

        try:
            img_fname = self._img_fnames[self._img_idx]

            self.image.load_img(img_fname)
            self.fname_list.set_idx(self._img_idx)

            if self._labeler:
                labels = self._labeler.get_labels(img_fname)
                self.current_labels.add_items(labels)
        except IndexError:
            logger.warning('no images to display')

    def _next_img(self):
        """
        Load the next image
        """
        self._img_idx += 1

        # wrap around if necessary
        if self._img_idx >= len(self._img_fnames):
            self._img_idx = 0

        self._load()

    def _prev_img(self):
        """
        Load the previous image
        """
        self._img_idx -= 1

        # wrap around if necessary
        if self._img_idx < 0:
            self._img_idx = len(self._img_fnames) - 1

        self._load()

    def _jump_to_img(self, fname):
        """
        Load/jump to the file fname

        :param fname: The name of the file to jump to
        """
        self._img_idx = self._img_fnames.index(fname)
        self._load()

    def _label_with_speech(self):
        """
        Convert speech to text and use each word
        in the text as a label
        """
        # convert speech to labels
        self.statusbar.showMessage('listening for classification labels')
        labels = self._listener.get_words()
        self.statusbar.clearMessage()

        # make sure the labeler exists
        if not self._labeler:
            self._get_labels_fname()

        # add labels
        for label in labels:
            self._labeler.add_label(self._img_fnames[self._img_idx], label)
            self._labeler.save()

        # show labels for this image
        self.current_labels.add_items(labels)
        self._refresh_classes()

    def _key_pressed(self, e):
        """
        Perform actions based on key press

        :param e: The event
        """
        key = e.key()

        if key == QtCore.Qt.Key_Right or key == QtCore.Qt.Key_Down:
            self._next_img()
        elif key == QtCore.Qt.Key_Left or key == QtCore.Qt.Key_Up:
            self._prev_img()
        elif key == QtCore.Qt.Key_Control:
            # only begin labeling if there are images
            if self._img_fnames:
                self._label_with_speech()

    def eventFilter(self, source, event):
        """
        Process an event

        :param source: The event source
        :param event: The event
        """
        if event.type() == QtCore.QEvent.KeyPress:
            self._key_pressed(event)
            return True

        return super(self.__class__, self).eventFilter(source, event)
