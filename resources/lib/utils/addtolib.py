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

    # Nebolo by lepsie davat rovno .strm subory bez adresara? Pripadne optional?
    if not xbmcvfs.exists(dirName):
        xbmcvfs.mkdir(dirName)
    strmFileName    = os.path.join(dirName, originalTitle + ' (' + year + ')' + '.strm')
    logger.debug("%s %s" % (strmFileName, moviePath))
    file            = xbmcvfs.File(strmFileName, 'w')
    file.write(str(moviePath))
    file.close()
    # Toto by som asi nerobil zakazdym, ak ma library viac poloziek, moze to kus trvat. Lepsie je nechat si to pustat na pozadi
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
    # xbmcgui.Dialog().ok(dbtype, 'Original title: ' + originalTitle, 'TV Show title: ' + tvShowTitle, 'Seasons count: ' + seasonsCount)


def add_to_library():
    logger.debug("add to lib called")
    # DialogRenderer.ok('Info', 'OK')
    # Check settings, whether library paths are set up corretly
    if dbtype == 'movie':
        if settings['movielFolder'] == '':
            show_settings()
            # tu by to mozno chcelo najst sposob ako otvorit settings rovno na danej karte
        mf = settings['movielFolder']
        if mf != '':
            addMovie(mf)

    if dbtype == 'tvshow':
        DialogRenderer.ok(addon.getLocalizedString(30030), addon.getLocalizedString(30031))
        #if addon.getSetting("tvshowsFolder") == '':
        #    addon.openSettings()
        #tf = addon.getSetting("tvshowsFolder")
        #if tf != '':
        #    addTVShow(tf)