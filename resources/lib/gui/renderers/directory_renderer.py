import contextlib

import xbmcplugin

from resources.lib.const import COMMAND, FILTER_TYPE, ROUTE, COLLECTION, LANG, SETTINGS, explicit_genres, api_genres, \
    STRINGS
from resources.lib.gui import MoviesItem, SettingsItem, SearchItem, DirectoryItem, TvShowsItem, MainMenuFolderItem, \
    WatchHistoryItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import show_settings, router_url_from_string, get_string
from resources.lib.utils.url import Url
from resources.lib.utils.csfd_tips import get_csfd_tips


class DirectoryRenderer(Renderer):
    def __init__(self, router, on_a_to_z_menu):
        super(DirectoryRenderer, self).__init__(router)
        self._on_a_to_z_menu = on_a_to_z_menu

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
            WatchHistoryItem(url=router_url_from_string(ROUTE.WATCHED))(self.handle)
            SettingsItem(url=self._router.url_for(self.command, COMMAND.OPEN_SETTINGS))(self.handle)
        return

    def command(self, what):
        xbmcplugin.endOfDirectory(self.handle)
        if what == COMMAND.OPEN_SETTINGS:
            show_settings()

    def media_menu(self, collection):
        with self.start_directory(self.handle):
            SearchItem(url=self._router.url_for(self.search, collection))(self.handle)
            DirectoryItem(title=get_string(LANG.POPULAR), url=router_url_from_string(ROUTE.POPULAR, collection))(self.handle)
            DirectoryItem(title=get_string(LANG.A_Z), url=self._url_for(self.a_to_z_menu, collection))(self.handle)
            DirectoryItem(title=get_string(LANG.GENRE), url=self._url_for(self.genre_menu, collection))(self.handle)
            self.add_extra_items(collection)

    def add_extra_items(self, collection):
        if collection == COLLECTION.MOVIES:
            DirectoryItem(title=get_string(LANG.CSFD_TIPS), url=self._router.url_for(self.csfd_tips, collection))(self.handle)

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
        genres.sort()
        with self.start_directory(self.handle):
            for genre in genres:
                DirectoryItem(title=get_string(genre),
                              url=router_url_from_string(ROUTE.FILTER, collection, FILTER_TYPE.GENRE,
                                                         api_genres[genre])
                              )(self.handle)

    def a_to_z_menu(self, collection):
        import string
        filter_type = FILTER_TYPE.STARTS_WITH
        zero_nine = get_string(LANG.ZERO_NINE)
        letter_counts = self._on_a_to_z_menu(collection, filter_type, [c for c in string.ascii_uppercase] + [zero_nine])
        with self.start_directory(self.handle):
            DirectoryItem(title=self._a_to_z_title(get_string(LANG.ZERO_NINE), letter_counts.get(zero_nine)),
                          url=router_url_from_string(ROUTE.FILTER, collection, filter_type,
                                                     zero_nine))(self.handle)
            for c in string.ascii_uppercase:
                DirectoryItem(title=self._a_to_z_title(c, letter_counts.get(c)), url=self._url_for(self.a_to_z_submenu, collection, c))(
                    self.handle)

    @staticmethod
    def _a_to_z_title(letter, count):
        return STRINGS.A_TO_Z_TITLE.format(letter, str(count))

    def a_to_z_submenu(self, collection, previous_letter):
        import string
        filter_type = FILTER_TYPE.STARTS_WITH
        letter_counts = self._on_a_to_z_menu(collection, filter_type,
                                             [previous_letter + c for c in string.ascii_uppercase])
        with self.start_directory(self.handle):
            MainMenuFolderItem(url=router_url_from_string(ROUTE.CLEAR_PATH))(self.handle)
            SearchItem(title=get_string(LANG.SEARCH_FOR_LETTERS).format(letters=previous_letter),
                       url=router_url_from_string(ROUTE.FILTER, collection, filter_type, previous_letter))(self.handle)
            self._a_to_z_submenu_items(collection, filter_type, previous_letter, letter_counts)

    def _a_to_z_submenu_items(self, collection, filter_type, previous_letter, letter_counts):
        import string
        for c in string.ascii_uppercase:
            letters = previous_letter + c
            count = letter_counts.get(letters)

            if count > 0:
                url = router_url_from_string(ROUTE.FILTER, collection, filter_type,
                                             letters) if count <= settings.as_int(SETTINGS.A_Z_THRESHOLD) else self._url_for(self.a_to_z_submenu,
                                                                                       collection, letters)
                DirectoryItem(title=self._a_to_z_title(letters, count), url=url)(self.handle)

    def csfd_tips(self, collection):
        logger.debug('CSFD tips search opened')
        with self.start_directory(self.handle):
            for tip in get_csfd_tips():
                name = tip[0][:-7]
                name_quoted = tip[0][:-7].replace(' ', '%20')  # W/A to bypass quote_plus as it can't parse certain uni chars
                year = tip[0][-7:]
                tip_joined = name + year + ' [' + tip[1] + ']'
                DirectoryItem(title=tip_joined,
                              url=self._url_for(self.search_for_csfd_tips, collection, name_quoted))(self.handle)

    def search_for_csfd_tips(self, collection, item):
        self._router.go_to_route(ROUTE.SEARCH_RESULT, collection, item)
        # BUG stays in a loop if no items are returned from search

    # Cannot be more than 1 dir deep due to path history reset
    def search(self, collection):
        logger.debug('Search dialog opened')
        search_value = DialogRenderer.search()
        xbmcplugin.endOfDirectory(self.handle)
        if search_value:
            self._router.go_to_route(ROUTE.SEARCH_RESULT, collection, Url.quote_plus(search_value))
        else:
            logger.debug('No value for search. Returning.')
            self._router.replace_route(ROUTE.MEDIA_MENU, collection)
