from resources.lib.const import CACHE, STORAGE
from resources.lib.kodilogging import logger

from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_plugin_url

url_blacklist = [
    '/search/'
]


class PluginUrlHistory:
    def __init__(self):
        self._limit = CACHE.PLUGIN_URL_HISTORY_LIMIT
        if self.get_urls() is None:
            self.storage[STORAGE.PLUGIN_URL_HISTORY] = []

    @property
    def storage(self):
        return storage

    def add(self, url=None):
        is_added = self._add(url)
        self.storage[STORAGE.PLUGIN_LAST_URL_ADDED] = is_added
        return is_added

    def _add(self, url=None):
        if url is None:
            url = self.current()
        if not self.allowed(url):
            logger.debug('Blacklisted URL. Not adding.')
            return False
        if self.exists(url):
            logger.debug('Duplicate to last URL. Not adding.')
            return False

        urls = self.get_urls()
        if len(urls) >= self._limit:
            urls.pop(0)
        urls.append(url)
        logger.debug('URL added to history')
        self.storage[STORAGE.PLUGIN_URL_HISTORY] = urls
        return True

    def get(self, key):
        return self.storage.get(key)

    def get_urls(self):
        urls = self.storage.get(STORAGE.PLUGIN_URL_HISTORY)
        return urls if urls else []

    @property
    def current(self):
        return get_plugin_url()

    def previous(self, steps=0, skip_search=False):
        urls = self.skip_search_urls() if skip_search else self.get_urls()
        urls = [url for url in urls if url != self.current]
        return None if len(urls) == 0 else urls[-2 - steps]

    def exists(self, url):
        urls = self.get_urls()
        if len(urls) == 0:
            return False
        return url == urls[-1]

    def skip_search_urls(self):
        return [url for url in self.get_urls() if 'search' not in url]

    @staticmethod
    def allowed(url):
        for item in url_blacklist:
            if item in url:
                return False
        return True

    @staticmethod
    def current():
        return get_plugin_url()
