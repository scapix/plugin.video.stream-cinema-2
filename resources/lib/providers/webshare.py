"""
    Webshare link resolver.
"""

from __future__ import print_function

import hashlib
import xml.etree.ElementTree as ET

import requests
from simpleplugin import Plugin

from resources.lib.const import DOWNLOAD_TYPE, SETTINGS, CACHE
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import get_screen_width, get_screen_height, common_headers
from resources.lib.vendor.md5crypt import md5crypt

plugin = Plugin()

class Webshare:
    def __init__(self, username, password, token=None):
        self._username = username
        self._password = password
        self._token = token

    def __repr__(self):
        return self.__class__.__name__

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def token(self):
        return self._token

    @plugin.mem_cached(CACHE.EXPIRATION_TIME)
    def get_link_for_file_with_id(self, file_id, download_type=DOWNLOAD_TYPE.VIDEO_STREAM):
        """
        POST /api/file_link/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        data = {
            'ident': file_id,
            'download_type': download_type,
            'device_uuid': settings[SETTINGS.UUID],
            'device_res_x': get_screen_width(),
            'device_res_y': get_screen_height(),
        }
        response = self._post('/file_link/', data=data)
        root = ET.fromstring(response)
        link = root.find('link').text
        return link

    def _post(self, path, data=None):
        """
        :type data: dict
        """
        if data is None:
            data = {}
        data.setdefault('wst', self._token)
        headers = common_headers()
        headers.update({
            'Referer': 'https://webshare.cz/',
        })

        response = requests.post('https://webshare.cz/api{}'.format(path), data=data, headers=headers)
        return response.content

    def _get_salt(self):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/salt/', data={'username_or_email': self._username})
        root = ET.fromstring(response)
        salt = root.find('salt').text
        return salt

    def get_token(self):
        """
        POST /api/login/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        salt = self._get_salt()
        hashed = self._hash_password(self._password, salt)

        response = self._post('/login/', data={
            'username_or_email': self._username,
            'password': hashed,
            'keep_logged_in': 1,
        })
        root = ET.fromstring(response)
        token = root.find('token').text
        return token

    def get_user_data(self):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/user_data/')
        return response

    def is_vip(self):
        user_data = self.get_user_data()
        root = ET.fromstring(user_data)
        vip = root.find('vip').text
        return bool(vip)


    @classmethod
    def _hash_password(cls, password, salt):
        """Creates password hash used by Webshare API"""
        return hashlib.sha1(md5crypt(password, salt=salt).encode('utf-8')).hexdigest()
