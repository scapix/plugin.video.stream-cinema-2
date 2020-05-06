from simpleplugin import MemStorage
from simpleplugin import Plugin

from resources.lib.api import API
from resources.lib.const import CACHE
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import get_plugin_url

plugin = Plugin()


class Cache:
    def __init__(self, cache_id):
        self._id = cache_id
        self._storage = MemStorage(cache_id)

    def __setitem__(self, key, value):
        logger.debug('[Cache:%s] Set cache' % (self._id + '.' + key))
        self._storage[key] = value

    def __getitem__(self, key):
        logger.debug('[Cache:%s] Get cache' % (self._id + '.' + key))
        return self._storage[key]

    def __delitem__(self, key):
        del self._storage[key]

    def get(self, key):
        try:
            return self[key]
        except:
            return None


class CachedAPI(API):
    def __init__(self, _id, *args, **kwargs):
        self._id = _id
        super(CachedAPI, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__ + '.' + self._id

    @plugin.mem_cached(CACHE.EXPIRATION_TIME)
    def media_filter(self, *args, **kwargs):
        return super(CachedAPI, self).media_filter(*args, **kwargs)

    @plugin.mem_cached(CACHE.EXPIRATION_TIME)
    def next_page(self, *args, **kwargs):
        return super(CachedAPI, self).get(*args, **kwargs)


url_blacklist = [
    '/search/'
]


class PluginUrlHistory:
    def __init__(self):
        self._id = CACHE.PLUGIN_URL_HISTORY
        self._limit = CACHE.PLUGIN_URL_HISTORY_LIMIT
        self._storage = Cache(self._id)
        if self.get_urls() is None:
            self._storage['urls'] = []

    def add(self, url=None):
        is_added = self._add(url)
        self._storage['last_added'] = is_added
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
        self._storage['urls'] = urls
        return True

    def get(self, key):
        return self._storage.get(key)

    def get_urls(self):
        return self._storage.get('urls')


    @property
    def current(self):
        return get_plugin_url()

    def previous(self, skip_search=False):
        urls = self._skip_search_urls() if skip_search else self.get_urls()
        urls = [url for url in urls if url != self.current]
        index = -2 if self.get('last_added') else -1
        return None if len(urls) == 0 else urls[index]

    def exists(self, url):
        urls = self.get_urls()
        if len(urls) == 0:
            return False
        return url == urls[-1]

    def _skip_search_urls(self):
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
