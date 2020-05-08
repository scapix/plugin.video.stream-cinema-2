"""
    Stream cinema service.
"""

import logging

import xbmc

from resources.lib.defaults import Defaults
from resources.lib.kodilogging import setup_root_logger
from resources.lib.kodilogging import service_logger
from resources.lib.players.stream_cinema_player import StreamCinemaPlayer
from resources.lib.services.player_service import PlayerService

setup_root_logger()

service_logger.debug('Service started')
player_service = PlayerService(Defaults.api())
stream_cinema_player = StreamCinemaPlayer(service=player_service)

xbmc_monitor = xbmc.Monitor()
while not xbmc_monitor.abortRequested():
    # Do some stuff periodically. Since we have nothing to do for now, just block indefinitely.
    # Anyway we have to keep this blocked otherwise Player will get discarded.
    xbmc_monitor.waitForAbort()

# TODO: Fix warnings about some classes left in a memory:
# https://forum.kodi.tv/showthread.php?tid=307508&pid=2531105#pid2531105
service_logger.debug('Service stopped')
