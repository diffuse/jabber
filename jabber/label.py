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
            labels = list(self._labels[img_fname])
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
            self._labels[img_fname] = set()

        self._labels[img_fname].add(label)
        self._classes.add(label)

    def delete_label(self, img_fname, label):
        """
        Delete a label associated with an image filename

        :param img_fname: The image filename this label is associated with
        :param label: The label to delete
        """
        # TODO handle removing/keeping with class set
        try:
            self._labels[img_fname].remove(label)
        except (AttributeError, KeyError):
            logger.error(f'could not delete label {label} associated with img {img_fname}')

    def save(self):
        """
        Save labels to self._fname as JSON
        """
        # convert sets to lists
        labels = {fname: list(s) for fname, s in self._labels.items()}

        with open(self._fname, 'w') as f:
            json.dump(labels, f, indent=4, sort_keys=True)
            f.flush()
