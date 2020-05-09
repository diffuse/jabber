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
        self._keystrokes = list()

        try:
            # load the labels
            with open(self._fname, 'r') as f:
                self._labels = json.load(f)

                # populate the class set and convert label lists to sets
                for fname, labels in self._labels.items():
                    if type(labels) == list:
                        self._labels[fname] = set(labels)

                    self._classes.update(labels)

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

    def get_keystrokes(self):
        """
        Return a string of the keystrokes
        currently in the buffer
        """
        return ''.join(self._keystrokes)

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

    def add_class(self, class_name):
        """
        Add a class

        :param class_name: The class to add
        """
        self._classes.add(class_name)

    def match_class(self, key):
        """
        Add the key to the persistent keystroke buffer
        and compare to class set; return the appropriate
        class if the string created from the keystroke
        buffer has an unambiguous match

        If there is an running match with two strings that terminate
        differently (e.g. 'foo' -> ['foo', 'foo1']), the shorter string
        must be terminated with a space to match

        :param key: They key to create or add to the candidate string
        :return: class if matched, empty string otherwise
        """
        self._keystrokes.append(key)
        candidate = ''.join(self._keystrokes)
        matches = [c for c in self._classes if c.startswith(candidate.rstrip())]

        # unambiguous match
        if len(matches) == 1:
            self._keystrokes.clear()
            return matches[0]
        # potentially ambiguous match
        elif len(matches) > 1:
            # unsolvable without a space (e.g. 'ba' -> ['bar', 'baz'])
            if not candidate.endswith(' '):
                return ''
            # solvable if ending in space and a full match (e.g. 'bar ' -> ['bar', 'bar1'], choose 'bar')
            elif len(candidate) in [len(m.rstrip()) for m in matches]:
                self._keystrokes.clear()
                return min(matches, key=len)
            # not solvable yet
            else:
                return ''
        # no matches
        else:
            self._keystrokes.clear()

        return ''

    def delete_label(self, img_fname, label):
        """
        Delete a label associated with an image filename

        :param img_fname: The image filename this label is associated with
        :param label: The label to delete
        """
        try:
            self._labels[img_fname].remove(label)
        except (AttributeError, KeyError):
            logger.error(f'could not delete label {label} associated with img {img_fname}')

    def delete_class(self, class_name):
        """
        Delete a class

        :param class_name: The class to delete
        """
        try:
            # don't delete it if it's still a label somewhere
            for labels in self._labels.values():
                if class_name in labels:
                    logger.error(f'could not delete class {class_name}, it is still being used as a label')
                    return

            self._classes.remove(class_name)
        except KeyError:
            logger.error(f'could not delete class {class_name}')

    def save(self):
        """
        Save labels to self._fname as JSON
        """
        # convert sets to lists
        labels = {fname: list(s) for fname, s in self._labels.items()}

        with open(self._fname, 'w') as f:
            json.dump(labels, f, indent=4, sort_keys=True)
            f.flush()
