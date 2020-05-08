import xbmc


class StreamCinemaPlayer(xbmc.Player):
    def onPlayBackStarted(self):
        print('PLAYBACK STARTED')