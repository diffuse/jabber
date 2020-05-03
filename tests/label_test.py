import json
import os
import unittest
from jabber.label import Labeler


class LabelerTest(unittest.TestCase):
    def setUp(self):
        self.label_fname = '/tmp/test-labels.json'
        self.labeler = Labeler(self.label_fname)

    def tearDown(self):
        try:
            os.remove(self.label_fname)
        except OSError:
            pass

    def test_addLabel_AddsLabels(self):
        fname = 'foo.jpg'
        labels = ['bar', 'bar1']
        expected = {fname: labels}

        for label in labels:
            self.labeler.add_label(fname, label)

        self.assertEqual(self.labeler._labels, expected)

    def test_save_SavesLabels(self):
        labels = {'foo.jpg': ['foo', 'bar']}

        self.labeler._labels = labels
        self.labeler.save()

        with open(self.label_fname, 'r') as f:
            lines = f.read()
            self.assertEqual(json.loads(lines), labels)

    def test_init_LoadsExistingLabels(self):
        # save labels with one labeler
        labels = {'foo.jpg': ['foo', 'bar']}

        self.labeler._labels = labels
        self.labeler.save()

        # load them with another
        labeler = Labeler(self.label_fname)
        self.assertEqual(labeler._labels, labels)

    def test_init_HandlesEmptyFilename(self):
        labeler = Labeler('')
        self.assertEqual(len(labeler._labels), 0)

    def test_init_HandlesBadJson(self):
        # write some bad JSON to a test file
        bad_json_file = '/tmp/bad-json.json'
        with open(bad_json_file, 'w') as f:
            f.write('not JSON')
            f.flush()

        labeler = Labeler(bad_json_file)
        self.assertEqual(len(labeler._labels), 0)
