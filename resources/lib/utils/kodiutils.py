# -*- coding: utf-8 -*-
import re
import sys

import xbmc
import xbmcaddon
import xbmcgui
import logging
import json as json

import xbmcplugin

from resources.lib.const import PROTOCOL, REGEX

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


def replace_router_params(route_url, *args):
    matches = re.finditer(REGEX.ROUTER_PARAMS, route_url, re.MULTILINE)
    i = 0
    while True:
        match = re.search(REGEX.ROUTER_PARAMS, route_url, re.MULTILINE)
        if match is None:
            break
        start = match.start()
        end = match.end()
        route_url = route_url[:start] + str(args[i]) + route_url[end:]

        i += 1

    return route_url


def router_url_from_string(route_url, *args):
    return get_plugin_base_url() + replace_router_params(route_url, *args)


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
    return ADDON.getLocalizedString(string_id)


def get_kodi_version():
    return xbmc.getInfoLabel('System.BuildVersion')


def get_screen_width():
    return xbmc.getInfoLabel('System.ScreenWidth')


def get_os_version():
    return xbmc.getInfoLabel('System.BuildVersion')


def get_screen_height():
    return xbmc.getInfoLabel('System.ScreenHeight')


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
