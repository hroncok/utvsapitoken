import json
import time

import requests

from utvsapitoken.exceptions import *


class TokenClient:
    '''Class for making requests for tokens'''

    def __init__(self, check_token_uri=None, usermap_uri=None):
        self.turi = check_token_uri or \
            'https://auth.fit.cvut.cz/oauth/check_token'
        self.uuri = usermap_uri or \
            'https://kosapi.fit.cvut.cz/usermap/v1/people'

    @classmethod
    def raise_if_error(cls, info, e):
        if 'error' in info:
            msg = info['error']
            if 'error_description' in info:
                msg = info['error_description']
            raise e(msg)

    def token_to_info(self, token):
        '''For given token, produces an info dict'''
        r = requests.get(self.turi, {'token': token})
        info = json.loads(r.text)
        self.raise_if_error(info, TokenInvalid)
        if info['exp'] <= time.time():
            raise TokenExpired('Token is expired')

        if 'user_name' in info:
            pnum = self.pnum_from_username(info['user_name'], token)
            if pnum:
                info.update({'personal_number': pnum})

        return info

    def pnum_from_username(self, username, token):
        r = requests.get(self.uuri + '/' + username,
                         headers={'Authorization': 'Bearer %s' % token})
        info = json.loads(r.text)
        self.raise_if_error(info, UsermapError)
        try:
            return info['personalNumber']
        except KeyError:
            return None