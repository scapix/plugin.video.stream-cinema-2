from resources.lib.const import SERVICE_EVENT
from resources.lib.kodilogging import service_logger
from resources.lib.players import BasePlayer


class StreamCinemaPlayer(BasePlayer):
    def __init__(self, service, player_core=0):
        super(StreamCinemaPlayer, self).__init__(service, player_core)
        self._service = service

    def onAVStarted(self):
        service_logger.debug("onAVStarted")

    def onPlayBackStarted(self):
        service_logger.debug("Playback started")
        self._service.emit(SERVICE_EVENT.PLAYBACK_STARTED)

    def onPlayBackEnded(self):
        service_logger.debug("onPlayBackEnded")

    def onPlaybackStopped(self):
        service_logger.debug("onPlaybackStopped")

