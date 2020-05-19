import requests

from resources.lib.const import GITLAB_ENDPOINT, URL, GENERAL
from resources.lib.utils.kodiutils import user_agent, replace_url_params, datetime_from_iso


class GitLabAPI:
    PRIVATE_TOKEN = '2cXgXEfhyy6P-5nN3tbb'
    PROJECT_ID = '2'

    @property
    def headers(self):
        return {
            'User-Agent': user_agent(),
            'PRIVATE-TOKEN': self.PRIVATE_TOKEN
        }

    def _get(self, url):
        sanitized_url = url.strip('/')
        return requests.get(
            '{}/{}/'.format(URL.GITLAB_URL, sanitized_url),
            headers=self.headers,
            timeout=GENERAL.API_TIMEOUT
        )

    def get_latest_release(self):
        releases = self._get(replace_url_params(GITLAB_ENDPOINT.RELEASES, self.PROJECT_ID)).json()
        latest_release = max(releases, key=lambda x: datetime_from_iso(x['released_at']))
        if latest_release:
            return latest_release.get('tag_name')
