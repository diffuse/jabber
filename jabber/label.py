import json
import logging

logger = logging.getLogger(__name__)


class Labeler:
    def __init__(self, fname):
        """
        Init labeler

        :param fname: The name of the file to store labels in
        """
        self._fname = fname
        self._labels = dict()
        self._classes = set()

        try:
            with open(self._fname, 'r') as f:
                self._labels = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f'could not load existing labels in {fname}')
        except OSError:
            pass

    def get_labels(self, img_fname):
        """
        Get labels associated with this image

        :param img_fname: The image filename
        :return: The list of labels associated with this image
        """
        labels = list()

        try:
            labels = self._labels[img_fname]
        except KeyError:
            pass

        return labels

    def get_classes(self):
        """
        Get all unique classes

        :return: A set of all unique classes
        """
        return self._classes

    def add_label(self, img_fname, label):
        """
        Associate a label with an image filename

        If there are already labels associated with this img_fname,
        just append this label after them

        :param img_fname: The image filename this label is associated with
        :param label: The label
        """
        if img_fname not in self._labels:
            self._labels[img_fname] = list()

        self._labels[img_fname].append(label)
        self._classes.add(label)

    def save(self):
        """
        Save labels to self._fname as JSON
        """
        with open(self._fname, 'w') as f:
            json.dump(self._labels, f, indent=4, sort_keys=True)
            f.flush()
