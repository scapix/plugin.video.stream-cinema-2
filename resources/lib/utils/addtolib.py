from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.utils.kodiutils import get_string #, notification
from resources.lib.settings import settings
from resources.lib.kodilogging import logger
from resources.lib.const import SETTINGS
import xbmc
import xbmcvfs
from os.path import join

dbtype  = xbmc.getInfoLabel("ListItem.dbtype")

def add_movie(mf):
    logger.debug("---------------------------------")
    originalTitle   = xbmc.getInfoLabel("ListItem.Originaltitle").decode('utf-8')
    year            = xbmc.getInfoLabel("ListItem.Year").decode('utf-8')
    moviePath       = xbmc.getInfoLabel("ListItem.FileNameAndPath")

    dirName = mf + originalTitle + ' (' + year + ')'

    if not xbmcvfs.exists(dirName):
        xbmcvfs.mkdir(dirName)
    strmFileName    = join(dirName, originalTitle + ' (' + year + ')' + '.strm')
    logger.debug("%s %s" % (strmFileName, moviePath))
    file            = xbmcvfs.File(strmFileName, 'w')
    file.write(str(moviePath))
    file.close()
    # eventualne hodit notifikaciu
    # notification('Added to library', 'Movie %s was successfully added to library' % originalTitle)
    # notification(get_string(30405), get_string(30406) % originalTitle)
    xbmc.executebuiltin('UpdateLibrary(video)')

def addTVShow(tf):
    # ToDo:
    originalTitle   = xbmc.getInfoLabel("ListItem.TVShowTitle").decode('utf-8')
    tvShowTitle     = xbmc.getInfoLabel("ListItem.Title").decode('utf-8')
    year            = xbmc.getInfoLabel("ListItem.Year").decode('utf-8')
    tvShowPath      = xbmc.getInfoLabel("ListItem.FileNameAndPath")
    seasonsCount    = xbmc.getInfoLabel("ListItem.Property('TotalSeasons')")

    # ToDo: Create Tv Show directory and season subdirectories with episode links
    dirName = tf + tvShowTitle + ' (' + year + ')'


def add_to_library():
    logger.debug("add to lib called")
    # DialogRenderer.ok('Info', 'OK')
    # Check settings, whether library paths are set up corretly
    if dbtype == 'movie':
        mf = settings[SETTINGS.MOVIE_LIBRARY_FOLDER]
        if mf != '':
            add_movie(mf)
        # k tomuto else by nemalo prist, kedze sa robi check pred contextMenu
        # else:
        #     notification('Unknown library folder', "Please set up movie library folder in settings")
        #     show_settings()


    # ToDo:
    if (dbtype == 'tvshow' or dbtype == 'episode'):
        DialogRenderer.ok(get_string(30351), get_string(30352))
        #if addon.getSetting("tvshowsFolder") == '':
        #    addon.openSettings()
        #tf = addon.getSetting("tvshowsFolder")
        #if tf != '':
        #    addTVShow(tf)