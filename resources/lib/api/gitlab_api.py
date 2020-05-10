import requests

from resources.lib.const import GITLAB_ENDPOINT, URL, GENERAL
from resources.lib.utils.kodiutils import common_headers, replace_url_params


class GitLabAPI:
    PRIVATE_TOKEN = '2cXgXEfhyy6P-5nN3tbb'
    PROJECT_ID = '2'

    @property
    def headers(self):
        common = common_headers()
        common['PRIVATE-TOKEN'] = self.PRIVATE_TOKEN
        return common

    def _get(self, url):
        sanitized_url = url.strip('/')
        return requests.get(
            '{}/{}/'.format(URL.GITLAB_URL, sanitized_url),
            headers=self.headers,
            timeout=GENERAL.API_TIMEOUT
        )

    def get_latest_release(self):
        return self._get(replace_url_params(GITLAB_ENDPOINT.RELEASES, self.PROJECT_ID)).json()
