import asyncio
import json
import requests
import sys
import urllib
import websockets

from mimi.accesstoken import AccessToken

class SpeechRecognitionWebsocket():
    __SEND_CHUNK_SIZE = 1024

    def __init__(self, auth_config):
        self.__access_token = AccessToken(auth_config)
        self.__ws = None

    async def open(self, lang='ja', ctype='pcm', rate=16000):
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
                'Authorization':  f'Bearer {self.__access_token.get()}',
                'x-mimi-process': 'nict-asr',
                'x-mimi-input-language': lang,
                'Content-Type': f'audio/x-{ctype};bit=16;rate={str(rate)};channels=1',
            }
        )

    async def send(self, data):
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
            if file_size < sent_size + self.__SEND_CHUNK_SIZE:
                await self.__ws.send(data[sent_size:file_size])
            else:
                await self.__ws.send(data[sent_size:sent_size + self.__SEND_CHUNK_SIZE])
                
            sent_size += self.__SEND_CHUNK_SIZE

    async def send_break(self):
        """
        send break
        """

        await self.__ws.send(json.dumps({'command': 'recog-break'}))

    async def recv(self):
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

    def close(self):
        """
        close ws server
        """
        self.__ws.close()

class SpeechRecognition():
    def __init__(self, auth_config):
        self.__access_token = AccessToken(auth_config)

    def convert(self, data, lang='ja', ctype='pcm', rate=16000):
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
                'Authorization':  f'Bearer {self.__access_token.get()}',
                'x-mimi-process': 'nict-asr',
                'x-mimi-input-language': lang,
                'Content-Type': f'audio/x-{ctype};bit=16;rate={str(rate)};channels=1',
            },
            data=data
        )

        if res.status_code != 200:
            raise Exception(f'{sys._getframe().f_code.co_name}: status: {str(res.status_code)}')

        return res.json()
