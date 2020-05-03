import json
import os
import unittest
from jabber.label import Labeler


class LabelerTest(unittest.TestCase):
    def setUp(self):
        self.label_fname = '/tmp/test-labels.txt'
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
