import os
import xbmc
from resources.lib.kodilogging import logger
from resources.lib.players.stream_cinema import StreamCinemaPlayer

logger.debug('Service %s started' % os.path.basename(__file__))

player = StreamCinemaPlayer()

while not xbmc.abortRequested:
    xbmc.sleep(100)

logger.debug('Service %s stopped' % os.path.basename(__file__))