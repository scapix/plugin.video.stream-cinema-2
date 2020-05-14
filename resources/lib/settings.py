from functools import partial

from resources.lib.kodilogging import logger
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import get_settings, show_settings, set_settings, get_setting_as_bool, \
    get_setting_as_int


class Settings:
    def __setitem__(self, key, value):
        set_settings(key, value)

    def __getitem__(self, key):
        return get_settings(key)

    @staticmethod
    def as_bool(key):
        return get_setting_as_bool(key)

    @staticmethod
    def as_int(key):
        return get_setting_as_int(key)

    @staticmethod
    def show():
        show_settings()

    @staticmethod
    def dynamic(key):
        return partial(get_settings, key)

    def set_cache(self, key, value):
        self[key] = value
        storage[key] = value

    def load_to_cache(self, *args):
        for key in args:
            storage[key] = self[key]
            logger.debug('Loading to cache %s' % key)
            logger.debug(self[key])
            logger.debug(storage[key])


 settings = Settings()
