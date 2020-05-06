import contextlib

import xbmcplugin

from resources.lib.const import COMMAND, FILTER_TYPE, ROUTE
from resources.lib.gui import MoviesItem, SeriesItem, SettingsItem, SearchItem, DirectoryItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import show_settings, router_url_for, router_url_from_string, \
    go_to_plugin_url


class DirectoryRenderer(Renderer):
    def __init__(self, router):
        super(DirectoryRenderer, self).__init__(router)

    @staticmethod
    @contextlib.contextmanager
    def start_directory(handle, as_type=None):
        """Simple context manager that automatically ends the directory."""
        if as_type:
            xbmcplugin.setContent(handle, as_type)
        yield
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)

    def main_menu(self):
        logger.debug('Rendering main menu')
        with self.start_directory(self.handle):
            MoviesItem(url=self._router.url_for(self.media_menu, 'movies'))(self.handle)
            SeriesItem(url=self._router.url_for(self.media_menu, 'series'))(self.handle)
            SettingsItem(url=self._router.url_for(self.command, 'open-settings'))(self.handle)
        return

    def command(self, what):
        xbmcplugin.endOfDirectory(self.handle)
        if what == COMMAND.OPEN_SETTINGS:
            show_settings()

    def media_menu(self, collection):
        with self.start_directory(self.handle):
            SearchItem(url=self._router.url_for(self.search, collection))(self.handle)
            DirectoryItem(title="A-Z", url=self._url_for(self.a_to_z_menu, collection))(self.handle)
        return

    def a_to_z_menu(self, collection, callback):
        import string
        filter_type = FILTER_TYPE.STARTS_WITH_LETTER

        with self.start_directory(self.handle, as_type='videos'):
            DirectoryItem(title='0-9', url=self._url_for(callback, collection, filter_type, '0-9'))(self.handle)
            for c in string.ascii_uppercase:
                DirectoryItem(title=c, url=self._url_for(callback, collection, filter_type, c))(self.handle)

    def search(self, collection):
        logger.debug('Search dialog opened')
        search_value = DialogRenderer.search()
        xbmcplugin.endOfDirectory(self.handle)
        if search_value:
            self._router.go_to_route(ROUTE.SEARCH_RESULT, collection, search_value)
        else:
            logger.debug('No value for search. Returning.')
            self._router.back(skip_search=True)
