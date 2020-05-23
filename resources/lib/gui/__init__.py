import xbmcgui
import xbmcplugin   
import xbmc  

from resources.lib.const import LANG, STRINGS, ROUTE
from resources.lib.utils.kodiutils import router_url_from_string, get_string, ADDON


class DirectoryItem:
    TITLE = ''
    DIRECTORY = True
    ICON = ''
    URL = ''

    def __init__(self, title='', url='', icon=''):
        self._title = title if title else self.TITLE
        self._url = url if url else self.URL
        self._icon = icon if icon else self.ICON

    def __call__(self, handle, *args, **kwargs):
        url, li, is_folder = self.build()
        xbmcplugin.addDirectoryItem(handle, url, li, isFolder=is_folder)

    def build(self):
        inner_item = xbmcgui.ListItem(
            label=self._title,
            path=self._url,
        )
        inner_item.setArt({
            'icon': self._icon,
        })

        return self._url, inner_item, self.DIRECTORY,


class WatchHistoryItem(DirectoryItem):
    ICON = 'DefaultInProgressShows.png'
    TITLE = get_string(LANG.WATCH_HISTORY)


class SearchItem(DirectoryItem):
    ICON = 'DefaultAddonsSearch.png'
    TITLE = get_string(30204)


class MoviesItem(DirectoryItem):
    ICON = 'DefaultMovies.png'
    TITLE = get_string(30200)


class TvShowsItem(DirectoryItem):
    ICON = 'DefaultTvshows.png'
    TITLE = get_string(30201)


class MainMenuFolderItem(DirectoryItem):
    ICON = 'DefaultFolderBack.png'
    TITLE = get_string(30202)


class SeasonItem(DirectoryItem):
    ICON = 'DefaultTVShowTitle.png'


class SettingsItem(DirectoryItem):
    ICON = 'DefaultAddonService.png'
    TITLE = get_string(30208)
    DIRECTORY = False


class MediaItem(object):
    DIRECTORY = False

    def __init__(self, title, url=None, art=None, info_labels=None, stream_info=None, services=None):
        self._title = title
        self._url = url
        self._art = art
        self._info_labels = info_labels
        self._stream_info = stream_info
        self._services = services

    def __call__(self, handle):
        url, li, is_folder = self.build()
        xbmcplugin.addDirectoryItem(handle, url, li, isFolder=is_folder)

    def build(self):
        """Creates the ListItem together with metadata."""
        item = xbmcgui.ListItem(
            label=self._title,
            path=self._url,
        )
        if self._art:
            # Without this it clutters the logs with:
            # CreateLoader - unsupported protocol(plugin) in plugin://plugin.video.stream-cinema-2/select_stream/5eb4691439a9578cbf25d7f4
            # InputStream: Error opening, plugin://plugin.video.stream-cinema-2/select_stream/5eb4691439a9578cbf25d7f4
            # Kodi for some reason tries to load the Art from the movie.
            # We have to set only some attributes of the Art.
            item.setArt({
                'fanart': self._art.get('fanart'),
                'poster': self._art.get('poster'),
            })
        if self._info_labels:
            item.setInfo('video', self._info_labels)
        if self._stream_info:
            for key, value in self._stream_info.items():
                item.addStreamInfo(key, value)
        if self._services:
            item.setUniqueIDs({'imdb': 'tt' + str(self._services.get('imdb'))}, 'imdb')

        item.setProperty('IsPlayable', 'true')
        
        # '1234' is just an example, in add_to_library method I do not need any argument
        item.addContextMenuItems([(get_string(LANG.ADD_TO_LIBRARY), router_url_from_string(ROUTE.ADD_TO_LIBRARY, '1234'))])

        return self._url, item, self.DIRECTORY,


class TvShowMenuItem(MediaItem):
    DIRECTORY = True


class TvShowItem(MediaItem):
    def __init__(self, *args, **kwargs):
        super(TvShowItem, self).__init__(*args, **kwargs)


class InfoDialogType:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class InfoDialog:
    def __init__(self, message, heading=ADDON.getAddonInfo('name'), icon='', time=3000, sound=False):
        self._heading = heading
        self._message = message
        self._icon = InfoDialog._get_icon(icon)
        self._time = time
        self._sound = sound
        self._dialog = xbmcgui.Dialog()

    @staticmethod
    def _get_icon(icon):
        if icon == '':
            return ADDON.getAddonInfo('icon')
        elif icon == InfoDialogType.INFO:
            return xbmcgui.NOTIFICATION_INFO
        elif icon == InfoDialogType.WARNING:
            return xbmcgui.NOTIFICATION_WARNING
        elif icon == InfoDialogType.ERROR:
            return xbmcgui.NOTIFICATION_ERROR

    def notify(self):
        self._dialog.notification(self._heading, self._message, self._icon, self._time, sound=self._sound)
