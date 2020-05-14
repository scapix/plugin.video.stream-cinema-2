import datetime
import operator
import xbmc
from xbmcgui import Dialog
from resources.lib.const import STRINGS, SETTINGS, codecs, LANG
from resources.lib.utils.kodiutils import show_input, get_string, convert_size, make_table, \
    append_list_items_to_nested_list_items, convert_bitrate
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
        streams.sort(key=operator.itemgetter('size'), reverse=settings.as_int(SETTINGS.FILE_SIZE_SORT))
        audio_info_list = []
        for stream in streams:
            # Fix audio string that begins with the comma.
            audio_info = []
            for audio in stream.get('audio'):
                audio_info.append(STRINGS.AUDIO_INFO.format(audio.get('codec'), format(audio.get('channels'), '.1f'),
                                                            audio.get('language')))
            audio_info_list.append(' '.join(audio_info))
            quality = STRINGS.STREAM_TITLE_BRACKETS.format(stream.get('quality'))
            size = STRINGS.BOLD.format(convert_size(stream.get('size')))
            bitrate = STRINGS.STREAM_BITRATE_BRACKETS.format(
                convert_bitrate(stream.get('bitrate'))) if settings.as_bool(
                SETTINGS.SHOW_BITRATE) else ''
            codec = STRINGS.STREAM_TITLE_BRACKETS.format(codecs[stream.get('codec')]) if settings.as_bool(
                SETTINGS.SHOW_CODEC) else ''
            duration = STRINGS.BOLD.format(str(datetime.timedelta(seconds=int(stream.get('duration'))))) if settings.as_bool(
                                SETTINGS.SHOW_DURATION) else ''
            stream_labels.append([quality, codec, size, duration, bitrate])

        table = make_table(stream_labels)
        table = append_list_items_to_nested_list_items(table, audio_info_list)

        ret = Dialog().select(get_string(LANG.CHOOSE_STREAM), [STRINGS.TABLE_SPACES.join(item) for item in table])
        if ret < 0:
            return None
        return streams[ret]

    @staticmethod
    def keyboard(title, value='', hidden=False):
        keyboard = xbmc.Keyboard(value, title, hidden)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText().strip()
        return False

    @staticmethod
    def ok(heading, *args, **kwargs):
        return Dialog().ok(heading, *args, **kwargs)

    @staticmethod
    def ok_multi_line(heading, pairs):
        return DialogRenderer.ok(heading, STRINGS.NEW_LINE.join(pairs))
