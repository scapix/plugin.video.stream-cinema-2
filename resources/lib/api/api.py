"""
    Stream Cinema backend API.
"""

import requests

from resources.lib.const import ENDPOINT, GENERAL, ORDER
from resources.lib.utils.kodiutils import replace_url_params, user_agent
from resources.lib.settings import get_uuid

class API(object):
    def __init__(self, plugin_version, uuid, api_url):
        self._api_url = api_url
        self._plugin_version = plugin_version
        self._uuid = uuid

    @staticmethod
    def _build_url(*args):
        return '/'.join(args)

    # TODO: Refactor this somehow because _source is not in episode structure
    #  and this is being used in media item builder which works for all media types same way
    @staticmethod
    def get_source(item):
        source = item.get('_source')
        return source if source else item

    @staticmethod
    def get_hits(response):
        return response.get('hits')

    def post(self, url, body):
        return self._post(url, body)

    @staticmethod
    def common_headers():
        return {
            'User-Agent': user_agent(),
            'X-Uuid': get_uuid()
        }

    def _post(self, url_path, body):
        sanitized_api_path = self._api_url.strip('/')
        sanitized_url_path = url_path.strip('/')
        return requests.post(
            '{}/{}'.format(sanitized_api_path, sanitized_url_path),
            json=body,
            headers=self.common_headers(),
            timeout=GENERAL.API_TIMEOUT
        )

    def media_filter(self, collection, filter_name, filter_values, order=ORDER.ASCENDING):
        body = {
            "filter_values": filter_values
        }
        url = replace_url_params(ENDPOINT.FILTER, collection, filter_name, order)
        return self._post(url, body)

    def popular_media(self, collection):
        return self._post(replace_url_params(ENDPOINT.POPULAR, collection), None)

    def media_played(self, collection, media_id, uuid):
        return self._post(replace_url_params(ENDPOINT.MEDIA_PLAYED, collection, media_id, uuid), None)

    def media_detail(self, collection, media_id):
        return self._post(replace_url_params(ENDPOINT.MEDIA_DETAIL, collection, media_id), None)

    def get_filter_values_count(self, collection, filter_name, filter_values):
        body = {
            "filter_values": filter_values
        }
        return self._post(replace_url_params(ENDPOINT.FILTER_COUNT, collection, filter_name), body)

    def watched(self, uuid):
        return self._post(replace_url_params(ENDPOINT.WATCHED, uuid), None)

    def sort(self, collection, sort_type, order):
        return self._post(replace_url_params(ENDPOINT.SORT, collection, sort_type, order), None)

