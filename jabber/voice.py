import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, ambient_sample_secs=2):
        """
        Init Listener

        :param ambient_sample_secs: The number of seconds to sample to adjust for ambient noise
        """
        self._mic = sr.Microphone()
        self._recognizer = sr.Recognizer()

        logger.info('adjusting for ambient noise')
        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source, ambient_sample_secs)

    def get_words(self):
        """
        Return all words recorded in the
        last listen interval

        :return: The list recorded words
        """
        words = list()
        audio = None

        with self._mic as source:
            audio = self._recognizer.listen(source)

        try:
            if audio:
                words = self._recognizer.recognize_sphinx(audio).split()
        except sr.UnknownValueError:
            logging.error('could not understand speech')

        return words
