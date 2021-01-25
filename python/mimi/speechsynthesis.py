import json
import requests
import sys
import urllib

from mimi.accesstoken import AccessToken

class SpeechSynthesis():
    def __init__(self, auth_config):
        self.__access_token = AccessToken(auth_config)

    def convert(self, text, audio_format='WAV', audio_endian='Little', gender='male', age='20', native='yes', lang='ja', engine='nict'):
        """
        speech synthesis

        Parameters
        ----------
        text : str
            UTF-8
        audio_format : str
            WAV, RAW, ADPCM, Speex
        audio_endian : str
            Little, Big
        gender : str
            female, male
        age : int
            age
        native : str
            yes, no
        lang : str
            ja, en, id, ko, vi, my, th, zh, zh-TW
        engine : str
            nict

        Returns
        -------
        content : binary
            audio data
        """

        res = requests.post(
            url='https://tts.mimi.fd.ai/speech_synthesis',
            headers={
                'Authorization':  f'Bearer {self.__access_token.get()}',
            },
            data={
                'text' : text,
                'audio_format' : audio_format,
                'audio_endian' : audio_endian,
                'gender' : gender,
                'age' : str(age),
                'native' : native,
                'lang' : lang,
                'engine' : engine,
            }
        )

        if res.status_code != 200:
            raise Exception(f'{sys._getframe().f_code.co_name}: status: {str(res.status_code)}')

        return res.content
