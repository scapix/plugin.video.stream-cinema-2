import contextlib

import xbmcplugin
from xbmcgui import Dialog

from resources.lib.cache import Cache
from resources.lib.const import CACHE, FILTER_TYPE, COMMAND, ROUTE, STRINGS
from resources.lib.gui import MediaItem, FolderBackItem, DirectoryItem, MoviesItem, SeriesItem, SettingsItem, SearchItem
from resources.lib.utils.kodiutils import get_string, show_settings, show_input, go_to_plugin_url, router_url_for, \
    logger
from resources.lib.utils.url import Url








