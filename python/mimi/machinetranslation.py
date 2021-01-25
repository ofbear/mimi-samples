import json
import requests
import sys
import urllib

from mimi.accesstoken import AccessToken

class MachineTranslation():
    def __init__(self, auth_config):
        self.__access_token = AccessToken(auth_config)

    def convert(self, text, source_lang, target_lang):
        """
        speech synthesis

        Parameters
        ----------
        text : str
            UTF-8
        source_lang : str
            WAV, RAW, ADPCM, Speex
        target_lang : str
            Little, Big

        Returns
        -------
        result : str
            response data
        """

        res = requests.post(
            url='https://tra.mimi.fd.ai/machine_translation',
            headers={
                'Authorization':  f'Bearer {self.__access_token.get()}',
            },
            data={
                'text' : text,
                'source_lang' : source_lang,
                'target_lang' : target_lang,
            }
        )

        if res.status_code != 200:
            raise Exception(f'{sys._getframe().f_code.co_name}: status: {str(res.status_code)}')

        return res.content.decode('utf-8')
