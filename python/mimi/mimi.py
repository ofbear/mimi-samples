import json
import requests
import sys
import time
import websockets

class Mimi():
    __ASR_WS_SEND_CHUNK_SIZE = 1024

    def __init__(self, config):
        self.__CONFIG = config

    def check_expiration(self, json_data=None):
        if 'endTimestamp' in json_data and json_data['endTimestamp'] > int(time.time()):
            return True

        return False

    def access_token(self):
        """
        get accessToken

        Returns
        -------
        json_data : json
            response data
        """

        res = requests.post(
            url='https://auth.mimi.fd.ai/v2/token',
            data={
                'grant_type': 'https://auth.mimi.fd.ai/grant_type/client_credentials',
                'client_id': f'{self.__CONFIG["application_id"]}:{self.__CONFIG["client_id"]}',
                'client_secret': self.__CONFIG["client_secret"],
                'scope' : ';'.join(self.__CONFIG["scope"]),
            }
        )

        if res.status_code != 200:
            raise Exception(f'{sys._getframe().f_code.co_name}: status: {str(res.status_code)}')

        json_data = res.json()

        if json_data['status'] != 'success':
            raise Exception(f'{sys._getframe().f_code.co_name}: error: {json_data["error"]}')

        return json_data

    def tra(self, access_token, text, source_lang, target_lang):
        """
        machine translation

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
                'Authorization':  f'Bearer {access_token}',
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

    def tts(self, access_token, text, audio_format='WAV', audio_endian='Little', gender='male', age='20', native='yes', lang='ja', engine='nict'):
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
                'Authorization':  f'Bearer {access_token}',
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

    def asr(self, access_token, data, lang='ja', ctype='pcm', rate=16000):
        """
        connect ws server

        Parameters
        ----------
        lang : str
            input language
        ctype : str
            pcm, flac
        rate : int
            sampling rate

        Returns
        -------
        json_data : json
            response data
        """

        res = requests.post(
            url='https://service.mimi.fd.ai',
            headers={
                'Authorization':  f'Bearer {access_token}',
                'x-mimi-process': 'nict-asr',
                'x-mimi-input-language': lang,
                'Content-Type': f'audio/x-{ctype};bit=16;rate={str(rate)};channels=1',
            },
            data=data
        )

        if res.status_code != 200:
            raise Exception(f'{sys._getframe().f_code.co_name}: status: {str(res.status_code)}')

        return res.json()

    async def asr_ws_open(self, access_token, lang='ja', ctype='pcm', rate=16000):
        """
        connect ws server

        Parameters
        ----------
        lang : str
            input language
        ctype : str
            pcm, flac
        rate : int
            sampling rate

        Returns
        -------
        ws : obj
            websocket obj
        """

        self.__ws = await websockets.connect(
                'wss://service.mimi.fd.ai',
                extra_headers={
                'Authorization':  f'Bearer {access_token}',
                'x-mimi-process': 'nict-asr',
                'x-mimi-input-language': lang,
                'Content-Type': f'audio/x-{ctype};bit=16;rate={str(rate)};channels=1',
            }
        )

    async def asr_ws_send(self, data):
        """
        send data

        Parameters
        ----------
        data : binary
            send data
        """

        if self.__ws == None:
            raise Exception(f'{sys._getframe().f_code.co_name}: ws is none')

        file_size = len(data)
        sent_size = 0
        while sent_size < file_size:
            if file_size < sent_size + self.__ASR_WS_SEND_CHUNK_SIZE:
                await self.__ws.send(data[sent_size:file_size])
            else:
                await self.__ws.send(data[sent_size:sent_size + self.__ASR_WS_SEND_CHUNK_SIZE])
                
            sent_size += self.__ASR_WS_SEND_CHUNK_SIZE

    async def asr_ws_send_break(self):
        """
        send break
        """

        await self.__ws.send(json.dumps({'command': 'recog-break'}))

    async def asr_ws_recv(self):
        """
        send data

        Returns
        -------
        ws : obj
            websocket obj
        """

        if self.__ws == None:
            raise Exception(f'{sys._getframe().f_code.co_name}: ws is none')

        res = await self.__ws.recv()

        return json.loads(res)

    def asr_ws_close(self):
        """
        close ws server
        """
        self.__ws.close()

