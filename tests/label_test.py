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

    def test_getKeystrokes_GetsKeystrokeString(self):
        keystrokes = ['f', 'o', 'o']
        self.labeler._keystrokes = keystrokes

        self.assertEqual(self.labeler.get_keystrokes(), 'foo')

    def test_getKeystrokes_WithEmptyList_GetsEmptyString(self):
        keystrokes = list()
        self.labeler._keystrokes = keystrokes

        self.assertEqual(self.labeler.get_keystrokes(), '')

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

    def test_addClass_AddsClass(self):
        test_class = 'test'

        self.labeler.add_class(test_class)

        self.assertEqual(self.labeler._classes, {test_class})

    def test_matchClass_MatchesClass(self):
        self.labeler._classes = {'foo', 'bar', 'bar1', 'spam and', 'spam and eggs'}

        test_cases = [
            (['f'], 'foo'),
            (['b', 'a', 'r', ' '], 'bar'),
            (['b', 'a', 'r', '1'], 'bar1'),
            (['b', 'f'], ''),
            (['b', 'f', 'f'], 'foo'),
            (['b', ''], ''),
            (['b', ' '], ''),
            (['k', 'foo'], 'foo'),
            (['s', 'p', 'a', 'm', ' ', 'a', 'n', 'd', ' ', 'e'], 'spam and eggs'),
        ]

        for keystrokes, expected in test_cases:
            last_result = ''

            for keystroke in keystrokes:
                last_result = self.labeler.match_class(keystroke)

            self.assertEqual(last_result, expected)

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

    def test_deleteClass_DeletesClass(self):
        classes = {'foo', 'bar'}

        self.labeler._classes = classes
        self.labeler.delete_class('foo')

        self.assertEqual(self.labeler._classes, {'bar'})

    def test_deleteClass_DoesntDeleteClassWhenStillInUse(self):
        classes = {'foo', 'bar'}

        self.labeler._labels = {'test.jpg': classes}
        self.labeler._classes = classes
        self.labeler.delete_class('foo')

        self.assertEqual(self.labeler._classes, classes)

    def test_deleteClass_WithBadArgs_Ignores(self):
        classes = {'foo', 'bar'}
        self.labeler._classes = classes
        self.labeler.delete_class('not a class')

        self.assertEqual(self.labeler._classes, classes)

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
        self.assertEqual(labeler._labels, {fname: labels})
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
