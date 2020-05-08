from resources.lib.api.api import API
from resources.lib.const import CACHE
from simpleplugin import Plugin

plugin = Plugin()


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
