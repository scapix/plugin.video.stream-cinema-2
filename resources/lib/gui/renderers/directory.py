import contextlib

import xbmcplugin

from resources.lib.const import COMMAND, FILTER_TYPE, ROUTE, COLLECTION, LANG, SETTINGS, explicit_genres
from resources.lib.gui import MoviesItem, SettingsItem, SearchItem, DirectoryItem, TvShowsItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import show_settings, router_url_from_string, get_string


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
            MoviesItem(url=self._router.url_for(self.media_menu, COLLECTION.MOVIES))(self.handle)
            TvShowsItem(url=self._router.url_for(self.media_menu, COLLECTION.TV_SHOWS))(self.handle)
            SettingsItem(url=self._router.url_for(self.command, 'open-settings'))(self.handle)
        return

    def command(self, what):
        xbmcplugin.endOfDirectory(self.handle)
        if what == COMMAND.OPEN_SETTINGS:
            show_settings()

    def media_menu(self, collection):
        with self.start_directory(self.handle):
            SearchItem(url=self._router.url_for(self.search, collection))(self.handle)
            DirectoryItem(title=get_string(30210), url=self._url_for(self.a_to_z_menu, collection))(self.handle)
            DirectoryItem(title=get_string(30209), url=self._url_for(self.genre_menu, collection))(self.handle)

    def genre_menu(self, collection):
        genres = [LANG.ACTION, LANG.ANIMATED, LANG.ADVENTURE, LANG.DOCUMENTARY, LANG.DRAMA,
                  LANG.FANTASY, LANG.HISTORICAL, LANG.HORROR, LANG.MUSIC, LANG.IMAX, LANG.CATASTROPHIC, LANG.COMEDY,
                  LANG.SHORT, LANG.CRIME, LANG.MUSICAL, LANG.MYSTERIOUS, LANG.EDUCATIONAL, LANG.FAIRYTALE,
                  LANG.PSYCHOLOGICAL, LANG.JOURNALISTIC, LANG.REALITY, LANG.TRAVEL, LANG.FAMILY,
                  LANG.ROMANTIC, LANG.SCI_FI, LANG.COMPETITION, LANG.SPORTS, LANG.STAND_UP, LANG.TALK_SHOW,
                  LANG.TELENOVELA, LANG.THRILLER, LANG.MILITARY, LANG.WESTERN, LANG.BIOGRAPHICAL
                  ]

        if settings.as_bool(SETTINGS.EXPLICIT_CONTENT):
            genres = genres + explicit_genres
        genres = [get_string(genre) for genre in genres]
        genres.sort()
        with self.start_directory(self.handle):
            for genre in genres:
                DirectoryItem(title=genre,
                              url=router_url_from_string(ROUTE.FILTER, collection, FILTER_TYPE.GENRE, genre)
                              )(self.handle)

    def a_to_z_menu(self, collection):
        import string
        filter_type = FILTER_TYPE.STARTS_WITH_LETTER
        with self.start_directory(self.handle):
            DirectoryItem(title=get_string(30251),
                          url=router_url_from_string(ROUTE.FILTER, collection, filter_type, '0-9'))(self.handle)
            for c in string.ascii_uppercase:
                DirectoryItem(title=c, url=router_url_from_string(ROUTE.FILTER, collection, filter_type, c))(
                    self.handle)

    # Cannot be more than 1 dir deep due to path history reset
    def search(self, collection):
        logger.debug('Search dialog opened')
        search_value = DialogRenderer.search()
        xbmcplugin.endOfDirectory(self.handle)
        if search_value:
            self._router.go_to_route(ROUTE.SEARCH_RESULT, collection, search_value)
        else:
            logger.debug('No value for search. Returning.')
            self._router.replace_route(ROUTE.MEDIA_MENU, collection)
