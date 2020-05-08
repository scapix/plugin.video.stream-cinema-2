"""
    Stream cinema service.
"""

import logging

import xbmc

from resources.lib.kodilogging import setup_root_logger


setup_root_logger()
logger = logging.getLogger('stream-cinema-service')

logger.warning('Starting')



# Custom player mockup.
class MyPlayer(xbmc.Player):
    def onAVStarted(self):
        logger.warning("onAVStarted")

    def onPlayBackStarted(self):
        logger.warning("onPlayBackStarted")

    def onPlayBackEnded(self):
        logger.warning("onAVStarted")

    def onPlaybackStopped(self):
        logger.warning("onPlaybackStopped")





# Create player and just keep it in memory. That is all we need to receive events.
player = MyPlayer()


xbmc_monitor = xbmc.Monitor()
while not xbmc_monitor.abortRequested():
   # Do some stuff periodically. Since we have nothing to do for now, just block indefinitely.
   # Anyway we have to keep this blocked otherwise Player will get discarded.
   xbmc_monitor.waitForAbort()

# TODO: Fix warnings about some classes left in a memory:
# https://forum.kodi.tv/showthread.php?tid=307508&pid=2531105#pid2531105
logger.warning('Stopping')
