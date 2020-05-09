import glob
import logging
import os
from jabber.gui import MWBase, MWForm
from jabber.label import Labeler
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

        # signals
        self._connect_signals()

        # event filtering handling
        self.image.installEventFilter(self)

        # set focus policies
        self.image.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.fname_list.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.current_labels.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.classes.setFocusPolicy(QtCore.Qt.StrongFocus)

    def _connect_signals(self):
        """
        Connect signals to the appropriate slots
        """
        self.action_open.triggered.connect(self._get_input_files)
        self.action_set_labels_file.triggered.connect(self._get_labels_fname)
        self.fname_list.fname_selected.connect(self._jump_to_img)
        self.current_labels.item_deleted.connect(self._delete_label)
        self.classes.item_double_clicked.connect(self._add_label)
        self.classes.item_deleted.connect(self._delete_class)
        self.class_entry.returnPressed.connect(self._add_class_from_entry)

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

        # clear existing file list
        self.fname_list.clear()
        self._img_fnames.clear()

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

        if not labels_fname.lower().endswith('.json'):
            labels_fname += '.json'

        self._labeler = Labeler(labels_fname)
        self._load()

    def _add_label(self, label, save=True, refresh_class_list=True):
        """
        Add a label to the current image

        :param label: The label to add
        :param save: Flag to save labels after adding
        :param refresh_class_list: Flag to clear and repopulate class list after adding
        """
        # make sure the labeler exists
        while not self._labeler:
            self._get_labels_fname()

        try:
            # add the label
            img_fname = self._img_fnames[self._img_idx]
            self._labeler.add_label(img_fname, label)

            if save:
                self._labeler.save()

            # show labels for this image and refresh class lists
            self.current_labels.clear()
            self.current_labels.add_items(self._labeler.get_labels(img_fname))

            if refresh_class_list:
                self._refresh_classes()
        except IndexError:
            pass

    def _add_class(self, class_name):
        """
        Add a class to the labeler

        :param class_name: The class to add
        """
        # make sure the labeler exists
        while not self._labeler:
            self._get_labels_fname()

        # add the class
        self._labeler.add_class(class_name)
        self._refresh_classes()

    def _add_class_from_entry(self):
        """
        Convenience method to add class from line edit
        """
        class_name = self.class_entry.text()
        self._add_class(class_name)
        self.class_entry.clear()

    def _delete_label(self, label):
        """
        Delete a label associated with the current image

        :param label: The label to delete
        """
        try:
            img_fname = self._img_fnames[self._img_idx]

            if self._labeler:
                self._labeler.delete_label(img_fname, label)
                self._labeler.save()
        except IndexError:
            pass

    def _delete_class(self, class_name):
        """
        Delete a class associated with the labeler

        :param class_name: The class to delete
        """
        if self._labeler:
            self._labeler.delete_class(class_name)
            self._labeler.save()
            self._refresh_classes()

    def _refresh_classes(self):
        """
        Make sure the class list is current
        """
        if self._labeler:
            self.classes.clear()
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

    def _label_with_keystrokes(self, keystroke):
        """
        Try to match user keystrokes to existing classes
        and add a label if successful match found

        :param keystroke: The keystroke to use in matching
        """
        if self._labeler:
            match = self._labeler.match_class(keystroke)

            if match:
                self._add_label(match)

            self.statusbar.showMessage(self._labeler.get_keystrokes())

    def _reset_matching(self):
        """
        Reset keystroke matching
        """
        if self._labeler:
            self._labeler.reset_matching()
            self.statusbar.clearMessage()

    def _key_pressed(self, e):
        """
        Perform actions based on key press

        :param e: The event
        """
        key = e.key()
        text = e.text()

        if key in [QtCore.Qt.Key_Right, QtCore.Qt.Key_Down, QtCore.Qt.Key_Return]:
            self._next_img()
        elif key in [QtCore.Qt.Key_Left, QtCore.Qt.Key_Up]:
            self._prev_img()
        elif key == QtCore.Qt.Key_Escape:
            self._reset_matching()
        elif text.isalpha() or text.isspace():
            self._label_with_keystrokes(text)

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
