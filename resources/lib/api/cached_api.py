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

    @plugin.mem_cached(CACHE.EXPIRATION_TIME_BIGGER)
    def media_filter(self, *args, **kwargs):
        return super(CachedAPI, self).media_filter(*args, **kwargs)

    @plugin.mem_cached(CACHE.EXPIRATION_TIME_BIGGER)
    def next_page(self, *args, **kwargs):
        return super(CachedAPI, self).get(*args, **kwargs)

    @plugin.mem_cached(CACHE.EXPIRATION_TIME_BIGGER)
    def get_filter_values_count(self, *args, **kwargs):
        return super(CachedAPI, self).get_filter_values_count(*args, **kwargs)

    @plugin.mem_cached(CACHE.EXPIRATION_TIME_BIGGER)
    def media_detail(self, *args, **kwargs):
        return super(CachedAPI, self).media_detail(*args, **kwargs)

    @plugin.mem_cached(CACHE.EXPIRATION_TIME)
    def popular_media(self, *args, **kwargs):
        return super(CachedAPI, self).popular_media(*args, **kwargs)

