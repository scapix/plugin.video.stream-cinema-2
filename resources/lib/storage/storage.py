from simpleplugin import MemStorage
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import get_info


class Storage:
    def __init__(self):
        self._id = get_info('id')
        self._storage = MemStorage(self._id)

    @property
    def storage(self):
        return self._storage

    def __setitem__(self, key, value):
        logger.debug('[Cache:%s] Set cache' % (self._id + '.' + key))
        self._storage[key] = value

    def __getitem__(self, key):
        logger.debug('[Cache:%s] Get cache' % (self._id + '.' + key))
        return self._storage[key]

    def __delitem__(self, key):
        try:
            del self._storage[key]
        except:
            pass

    def get(self, key):
        try:
            return self[key]
        except:
            self[key] = {}
            return self[key]


storage = Storage()
