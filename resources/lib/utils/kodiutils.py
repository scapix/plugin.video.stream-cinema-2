# -*- coding: utf-8 -*-
import base64
import json
import math
import re
import sys
from datetime import datetime
from parser import ParserError

from dateutil.parser import parse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.const import PROTOCOL, REGEX, STRINGS, SETTINGS, api_genres

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

ADDON = xbmcaddon.Addon()


def notification(header, message, time=5000, icon=ADDON.getAddonInfo('icon'), sound=True):
    xbmcgui.Dialog().notification(header, message, icon, time, sound)


def show_settings():
    ADDON.openSettings()


def get_plugin_url():
    return sys.argv[0]


def get_plugin_base_url_with_path(path):
    sanitized_plugin_path = path.strip('/')
    return '{}/{}'.format(get_plugin_base_url(), sanitized_plugin_path)


def router_url_for(router, *args, **kwargs):
    return router.url_for(*args, **kwargs)


def replace_url_params(url, *args):
    i = 0
    while True:
        match = re.search(REGEX.ROUTER_PARAMS, url, re.MULTILINE)
        if match is None:
            break
        start = match.start()
        end = match.end()
        url = url[:start] + to_utf8_string(args[i]) + url[end:]

        i += 1

    return url


def to_utf8_string(val):
    if not isinstance(val, str):
        val = val.encode('utf8')
    return str(val)


def router_url_from_string(route_url, *args):
    return get_plugin_base_url() + replace_url_params(route_url, *args)


# You must end directory in order to update container
def go_to_plugin_url(url):
    xbmc.executebuiltin('Container.Update("%s")' % url)


# You must end directory in order to update container
def replace_plugin_url(url):
    xbmc.executebuiltin('Container.Update("%s", "replace")' % url)


def set_resolved_url(handle, url=None):
    if not url:
        xbmcplugin.setResolvedUrl(handle, True, xbmcgui.ListItem(path='Invalid_URL'))
    else:
        xbmcplugin.setResolvedUrl(handle, True, xbmcgui.ListItem(path=url))


def get_plugin_route():
    return get_plugin_url().replace(get_plugin_base_url(), '')


def show_input(heading, input_type=xbmcgui.INPUT_ALPHANUM):
    return xbmcgui.Dialog().input(heading, type=input_type)


def get_plugin_base_url():
    return '{}://{}'.format(PROTOCOL.PLUGIN, get_info('id'))


def get_info(info):
    return ADDON.getAddonInfo(info)


def get_settings(setting):
    return ADDON.getSetting(setting).strip()


def set_settings(setting, value):
    ADDON.setSetting(setting, str(value))


# It seems a bug in python https://bugs.python.org/issue27400
def parse_date(string_date):
    return parse(string_date, ignoretz=True)


def get_current_datetime_str():
    return datetime.now().strftime(STRINGS.DATETIME)


def datetime_from_iso(iso_date):
    return parse_date(iso_date)


def get_setting_as_datetime(setting):
    try:
        return parse_date(get_settings(setting))
    except:
        return None


def get_setting_as_bool(setting):
    return ADDON.getSettingBool(setting)


def get_setting_as_float(setting):
    try:
        return float(get_settings(setting))
    except ValueError:
        return 0


def get_setting_as_int(setting):
    try:
        return int(get_setting_as_float(setting))
    except ValueError:
        return 0


def get_string(string_id):
    return ADDON.getLocalizedString(string_id).encode('utf8')


def translate_string(s):
    regex = re.compile(r'\${(\d+)}', re.S)
    return regex.sub(lambda m: m.group().replace(m.group(), get_string(int(m.group()[2:-1])), 1), s)


def get_kodi_version():
    return xbmc.getInfoLabel('System.BuildVersion')


def get_screen_width():
    return xbmc.getInfoLabel('System.ScreenWidth')


def get_os_version():
    return xbmc.getInfoLabel('System.BuildVersion')


def get_screen_height():
    return xbmc.getInfoLabel('System.ScreenHeight')


def convert_size(size_bytes):
    if size_bytes == 0 or size_bytes is None:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def convert_bitrate(mbit):
    if mbit == 0 or mbit is None:
        return "0 Mbit/s"
    p = math.pow(1024, 2)
    s = round(mbit / p, 2)
    return "%s %s" % (s, "Mbit/s")


def make_table(matrix):
    matrix_length = len(matrix)
    if matrix_length == 0:
        return matrix
    for i in range(len(matrix[0])):
        longest = len(matrix[0][i])
        for r in range(matrix_length):
            length = len(matrix[r][i])
            if length > longest:
                longest = length

        for j, strings in enumerate(matrix):
            string = strings[i]
            diff = longest - len(string)
            spaces = ""
            for r in range(diff):
                spaces += STRINGS.TABLE_SPACES

            matrix[j][i] = spaces + string
    return matrix


def append_list_items_to_nested_list_items(_list, list_to_append):
    for i, nested_list in enumerate(_list):
        nested_list.append(list_to_append[i])
    return _list


def user_agent():
    return xbmc.getUserAgent()


def common_headers():
    return {
        'User-Agent': user_agent(),
        'X-Uuid': get_settings(SETTINGS.UUID)
    }


def delete_try(obj, key):
    try:
        del obj[key]
    except:
        pass


def apply_strings(text, *args):
    args = list(args)
    res = args.pop(0)
    for string in args:
        res = res.format(string)
    return res.format(*text)


def time_limit_expired(settings, limit):
    last_version_check = get_setting_as_datetime(settings)
    current_datetime = datetime.now()
    if last_version_check is None:
        return True
    return current_datetime - limit > last_version_check


def clear_kodi_addon_cache():
    xbmc.executebuiltin("UpdateLocalAddons")
    xbmc.executebuiltin('UpdateAddonRepos')


def get_genre_lang(api_genre):
    for key, genre in api_genres.items():
        if genre == api_genre:
            return get_string(key)
    return ''


def translate_genres(genre_list):
    return [get_genre_lang(genre) for genre in genre_list]

# def kodi_json_request(params):
#     data = json.dumps(params)
#     request = xbmc.executeJSONRPC(data)
#
#     try:
#         response = json.loads(request)
#     except UnicodeDecodeError:
#         response = json.loads(request.decode('utf-8', 'ignore'))
#
#     try:
#         if 'result' in response:
#             return response['result']
#         return None
#     except KeyError:
#         logger.warning("[%s] %s" %
#                        (params['method'], response['error']['message']))
#         return None
