import routing
import xbmcplugin

from resources.lib.const import STORAGE, ROUTE
from resources.lib.kodilogging import logger
from resources.lib.plugin_url_history import PluginUrlHistory
from resources.lib.storage.storage import storage
from resources.lib.utils.kodiutils import go_to_plugin_url, replace_plugin_url, router_url_from_string, set_resolved_url


class Router:
    def __init__(self):
        self._router = routing.Plugin()
        self._history = PluginUrlHistory()

    @property
    def handle(self):
        return self._router.handle

    @property
    def history(self):
        return self._history

    def back(self, steps=0, skip_search=False):
        previous_url = self._history.previous(steps, skip_search)
        logger.debug('Going to previous url %s', previous_url)
        self.replace(previous_url)

    def go(self, url):
        xbmcplugin.endOfDirectory(self.handle, cacheToDisc=False)
        logger.debug('Going to url: %s' % url)
        go_to_plugin_url(url)

    def replace(self, url=None):
        xbmcplugin.endOfDirectory(self.handle, cacheToDisc=False)
        url = self._history.current() if url is None else url
        logger.debug('Replacing url {} with {}'.format(self._history.current(), url))
        replace_plugin_url(url)

    def add_route(self, *args, **kwargs):
        return self._router.add_route(*args, **kwargs)

    def route(self, *args, **kwargs):
        return self._router.route(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self._router.run(*args, **kwargs)

    def url_for(self, *args, **kwargs):
        return self._router.url_for(*args, **kwargs)

    def go_to_route(self, *args):
        self.go(router_url_from_string(*args))

    # After redirect it also resets KODI path history a.k.a "back" action takes you to root path
    def replace_route(self, *args):
        xbmcplugin.endOfDirectory(self.handle, cacheToDisc=False)
        self.replace(router_url_from_string(*args))

    def set_resolved_url(self, url=None):
        set_resolved_url(self.handle, url)


