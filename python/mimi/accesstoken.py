import json
import requests
import sys
import threading
import time

class AccessToken():
    __singleton = None
    __new_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls.__new_lock:
            if cls.__singleton == None:
                cls.__singleton = super(AccessToken, cls).__new__(cls)
            return cls.__singleton

    def __init__(self, config):
        self.__CONFIG = config
        self.__end_time_stamp = 0
        self.__access_token = ''
    
    def get(self):
        """
        get accessToken

        Returns
        -------
        access_token : str
            access token
        """

        if self.__end_time_stamp > int(time.time()):
            return self.__access_token

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
            raise Exception(f'{sys._getframe().f_code.co_name}: error: {error}')
            
        self.__end_time_stamp = json_data['endTimestamp']
        self.__access_token = json_data['accessToken']

        return self.__access_token
