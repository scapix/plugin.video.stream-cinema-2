import operator

import xbmc
from xbmcgui import Dialog

from resources.lib.const import STRINGS, SETTINGS
from resources.lib.utils.kodiutils import show_input, get_string, convert_size, make_table, \
    append_list_items_to_nested_list_items
from resources.lib.settings import settings

class DialogRenderer:

    @staticmethod
    def search():
        search_value = show_input(get_string(30207))
        if search_value:
            return search_value

    @staticmethod
    def choose_video_stream(streams):
        stream_labels = []
        streams.sort(key=operator.itemgetter('size'), reverse=settings.as_bool(SETTINGS.SORT_DESCENDING))
        audio_info_list = []
        for stream in streams:
            # Fix audio string that begins with the comma.
            audio_info = []
            for audio in stream.get('audio'):
                audio_info.append('[I][{} {} {}][/I]'.format(audio.get('codec'), format(audio.get('channels'), '.1f'), audio.get('language')))
            audio_info_list.append(' '.join(audio_info))
            quality = STRINGS.STREAM_TITLE_BRACKETS.format(stream.get('quality'))
            size = STRINGS.BOLD.format(convert_size(stream.get('size')))
            stream_labels.append([quality, size])

        table = make_table(stream_labels)
        table = append_list_items_to_nested_list_items(table, audio_info_list)

        ret = Dialog().select('Choose the stream', ["   ".join(item) for item in table])
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

    @staticmethod
    def ok(heading, text):
        return Dialog().ok(heading, text)
