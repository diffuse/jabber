from unittest import mock, TestCase
from jabber import voice


class TestVoice(TestCase):
    def setUp(self):
        with mock.patch('speech_recognition.Microphone', autospec=True):
            with mock.patch('speech_recognition.Recognizer', autospec=True):
                self.listener = voice.Listener(ambient_sample_secs=0)

    def test_getWords_GetsWords(self):
        stt = 'these are some test labels'
        expected = ['these', 'are', 'some', 'test', 'labels']
        self.listener._recognizer.recognize_sphinx.return_value = stt

        words = self.listener.get_words()

        self.assertEqual(words, expected)
