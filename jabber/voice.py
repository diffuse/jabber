import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self):
        self._mic = sr.Microphone()

        # configure recognizer to pick up short words/phrases
        self._recognizer = sr.Recognizer()
        self._recognizer.pause_threshold = 0.4
        self._recognizer.phrase_threshold = 0.3
        self._recognizer.non_speaking_duration = 0.3

        self.adjust_for_ambient_noise()

    def adjust_for_ambient_noise(self, sample_secs=2):
        """
        Adjust recognizer for ambient sound

        :param sample_secs: The number of seconds to sample to adjust for ambient noise
        """
        logger.info(f'listening for {sample_secs}s to adjust for ambient noise')
        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source, sample_secs)

    def get_words(self, timeout=1.0):
        """
        Return all words recorded in the
        last listen interval

        :param timeout: The time, in seconds, to wait before ending listen period
        :return: The list recorded words
        """
        words = list()

        try:
            audio = None

            with self._mic as source:
                audio = self._recognizer.listen(source, timeout=timeout)

            if audio:
                words = self._recognizer.recognize_sphinx(audio).split()
        except sr.WaitTimeoutError:
            logger.error('timed out waiting for speech')
        except sr.UnknownValueError:
            logger.error('could not understand speech')

        return words
