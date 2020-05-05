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

    def test_getLabels_GetsLabels(self):
        fname = 'foo.jpg'
        labels = ['bar', 'bar1']
        self.labeler._labels = {fname: labels}

        self.assertEqual(self.labeler.get_labels(fname), labels)

    def test_getLabels_WithMissingFname_GetsEmptyList(self):
        self.assertEqual(self.labeler.get_labels(''), [])

    def test_addLabel_AddsLabels(self):
        fname = 'foo.jpg'
        labels = {'bar', 'bar1'}
        expected = {fname: labels}

        for label in labels:
            self.labeler.add_label(fname, label)

        self.assertEqual(self.labeler._labels, expected)

    def test_addLabel_WithDuplicateLabels_Ignores(self):
        fname = 'foo.jpg'

        for label in ['bar', 'bar']:
            self.labeler.add_label(fname, label)

        self.assertEqual(self.labeler._labels, {fname: {'bar'}})

    def test_addLabel_UpdatesClassSet(self):
        classes = {'bar', 'bar1'}

        for label in classes:
            self.labeler.add_label('', label)

        self.assertEqual(self.labeler.get_classes(), classes)

    def test_deleteLabel_DeletesLabel(self):
        fname = 'foo.jpg'
        labels = {'bar', 'bar1'}

        self.labeler._labels = {fname: labels}
        self.labeler.delete_label(fname, 'bar')

        self.assertEqual(self.labeler._labels[fname], {'bar1'})

    def test_deleteLabel_WithBadArgs_Ignores(self):
        fname = 'foo.jpg'
        labels = {'bar', 'bar1'}
        self.labeler._labels = {fname: labels}
        self.labeler.delete_label('not a filename', 'bar')
        self.labeler.delete_label('foo.jpg', 'not a label')

        self.assertEqual(self.labeler._labels[fname], labels)

    def test_save_SavesLabels(self):
        fname = 'foo.jpg'
        labels = {'foo', 'bar'}
        expected = {fname: list(labels)}

        self.labeler._labels = {fname: labels}
        self.labeler.save()

        with open(self.label_fname, 'r') as f:
            self.assertEqual(json.load(f), expected)

    def test_init_LoadsExistingLabels(self):
        # save labels with one labeler
        fname = 'foo.jpg'
        labels = {'foo', 'bar'}
        expected = {fname: list(labels)}

        self.labeler._labels = {fname: labels}
        self.labeler.save()

        # load them with another
        labeler = Labeler(self.label_fname)
        self.assertEqual(labeler._labels, expected)
        self.assertEqual(labeler._classes, labels)

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
