from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.utils.kodiutils import show_settings
from resources.lib.settings import settings
from resources.lib.kodilogging import logger
import xbmc
import xbmcaddon
import xbmcvfs
import os

addon   = xbmcaddon.Addon()
dbtype  = xbmc.getInfoLabel("ListItem.dbtype")

def addMovie(mf):
    logger.debug("---------------------------------")
    originalTitle   = xbmc.getInfoLabel("ListItem.Originaltitle").decode('utf-8')
    year            = xbmc.getInfoLabel("ListItem.Year").decode('utf-8')
    moviePath       = xbmc.getInfoLabel("ListItem.FileNameAndPath")

    dirName = mf + originalTitle + ' (' + year + ')'

    if not xbmcvfs.exists(dirName):
        xbmcvfs.mkdir(dirName)
    strmFileName    = os.path.join(dirName, originalTitle + ' (' + year + ')' + '.strm')
    logger.debug("%s %s" % (strmFileName, moviePath))
    file            = xbmcvfs.File(strmFileName, 'w')
    file.write(str(moviePath))
    file.close()
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
        if settings['movielFolder'] == '':
            show_settings()
        mf = settings['movielFolder']
        if mf != '':
            addMovie(mf)

    # ToDo:
    if (dbtype == 'tvshow' or dbtype == 'episode'):
        DialogRenderer.ok(addon.getLocalizedString(30351), addon.getLocalizedString(30352))
        #if addon.getSetting("tvshowsFolder") == '':
        #    addon.openSettings()
        #tf = addon.getSetting("tvshowsFolder")
        #if tf != '':
        #    addTVShow(tf)