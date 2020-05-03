import json


class Labeler:
    def __init__(self, fname):
        """
        Init labeler

        :param fname: The name of the file to store labels in
        """
        self._fname = fname
        self._labels = dict()

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

    def save(self):
        """
        Save labels to self._fname as JSON
        """
        labels_json = json.dumps(self._labels)

        with open(self._fname, 'w') as f:
            f.writelines(labels_json)
            f.flush()
