"""
    Stream Cinema backend API.
"""

import requests

from resources.lib.const import ENDPOINT
from resources.lib.utils.kodiutils import get_kodi_version


class API(object):
    def __init__(self, plugin_version, uuid, api_url):
        self._api_url = api_url
        self._plugin_version = plugin_version
        self._uuid = uuid

    @property
    def user_agent(self):
        return '{} ver{}'.format(get_kodi_version(), self._plugin_version)

    @property
    def common_headers(self):
        return {
            'User-Agent': self.user_agent,
            'X-Uid': self._uuid
        }

    def media_filter(self, collection, filter_name, value):
        url = self._build_url(ENDPOINT.MEDIA, collection, ENDPOINT.FILTER, filter_name, value)
        return self._get(url)

    @staticmethod
    def _build_url(*args):
        return '/'.join(args)

    def get(self, url):
        return self._get(url)

    def _get(self, url_path):
        sanitized_api_path = self._api_url.strip('/')
        sanitized_url_path = url_path.strip('/api')
        return requests.get(
            '{}/{}/'.format(sanitized_api_path, sanitized_url_path),
            headers=self.common_headers,
        )
