import xbmc
import xbmcgui
from xbmcgui import Dialog

from resources.lib.const import ROUTE, STRINGS
from resources.lib.gui.renderers import Renderer
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import show_input, get_string, go_to_plugin_url, router_url_for, \
    router_url_from_string


class DialogRenderer:

    @staticmethod
    def search():
        search_value = show_input(get_string(30207))
        if search_value:
            return search_value

    @staticmethod
    def choose_video_stream(streams):
        stream_labels = []
        for stream in streams:
            # Fix audio string that begins with the comma.
            audio_list = [a for a in stream['ainfo'].split(',') if a]

            stream_labels.append(
                STRINGS.STREAM_TITLE.format(
                    quality=stream['quality'],
                    lang=stream['lang'],
                    size=stream['size'],
                    ainfo=','.join(audio_list),
                )
            )

        ret = Dialog().select('Choose the stream', stream_labels)
        if ret < 0:
            return None
        return streams[ret]

    @staticmethod
    def keyboard(title):
        keyboard = xbmc.Keyboard('', title)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText()
            if search_entered == 0 or search_entered is None:
                return False
            return search_entered
        return False

