import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
from xml.etree import ElementTree as ET
import hashlib
from crypto.md5crypt import md5crypt
from string import ascii_uppercase
import re

addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')
hotshot_url = 'https://plugin.sc2.zone'
ws_api = 'https://webshare.cz/api'
UA = "KODI/18.6 (Windows; U; Windows NT; en) ver1.3.26"
realm = ':Webshare:'
base_url = sys.argv[0]

import simplecache

cache = simplecache.SimpleCache()
prefix = addon.getAddonInfo('id')

def set_cache(key, value):
	cache.set(prefix + "." + key, value)

def get_cache(key):
	return cache.get(prefix + "." + key)

def ws_api_request(url, data):
	return requests.post(ws_api + url, data=data)

def infoDialog(message,
	heading=addon.getAddonInfo('name'),
	icon='',
	time=3000,
	sound=False):
	if icon == '':
		icon = icon = addon.getAddonInfo('icon')
	elif icon == 'INFO':
		icon = xbmcgui.NOTIFICATION_INFO
	elif icon == 'WARNING':
		icon = xbmcgui.NOTIFICATION_WARNING
	elif icon == 'ERROR':
		icon = xbmcgui.NOTIFICATION_ERROR
	dialog = xbmcgui.Dialog()
	dialog.notification(heading, message, icon, time, sound=sound)

def login():
	username = addon.getSetting('wsuser')
	password = addon.getSetting('wspass')
	if username == '' or password == '':
		infoDialog('Please fill in credentials', sound=True)
		xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon.getAddonInfo('id'))
		return
	req = ws_api_request('/salt/', { 'username_or_email': username })
	salt = ET.fromstring(req.text).find('salt').text
	pass_digest = get_pass_digest(username, realm, password, salt)
	req = ws_api_request('/login/', { 'username_or_email': username, 'password': pass_digest['password'], 'digest': pass_digest['digest'], 'keep_logged_in': 1 })
	token = ET.fromstring(req.text).find('token').text
	addon.setSetting('token', token)
	return token

def get_stream_url(ident):
	token = addon.getSetting('token')
	if len(token) == 0:
		token = login()
	if token:
		req = ws_api_request('/file_link/', { 'wst': token, 'ident': ident })
		link = ET.fromstring(req.text).find('link').text
		return link

def get_pass_digest(username, realm, password, salt):
	encrypted_pass = hashlib.sha1(md5crypt(password.encode('utf-8'), salt.encode('utf-8'))).hexdigest()
	return { 'password': encrypted_pass, 'digest': hashlib.md5(username.encode('utf-8') + realm + encrypted_pass.encode('utf-8')).hexdigest() }

def api_request(url):
	url = hotshot_url + url
	try:
		return requests.get(url=url).json()
	except Exception as e:
		pass
	return 

def get_media_data(url):
	data = api_request(url)
	set_cache('media', data)
	return data

def get_media_from_cache(mediaId):
	mediaList = get_cache('media')
	for media in mediaList['data']:
		if media['id'] == mediaId:
			return media


def render_item(d, folder = True):
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=d['url'], listitem=d['item'], isFolder=folder)
		

def build_item(name, action, action_value = ''):
	return { 
		'item': xbmcgui.ListItem(add_translations(name), iconImage='DefaultVideo.png', offscreen=True),
		'url': build_plugin_url({ 'action': action, 'action_value': action_value })
	}

def build_plugin_url(query):
    return base_url + '?' + Url.encode(query)

def add_translations(s):
	regex = re.compile(r'\$(\d+)', re.S)
	return regex.sub(lambda m: m.group().replace(m.group(),addon.getLocalizedString(int(m.group()[1:])),1), s)

def page_info(page, pageCount):
	return ' ('+ page + '/' + pageCount +') '

def stream_title(stream):
	return "[B][" + stream['lang'] + '] ' + stream['quality'] + '[/B] - ' + stream['size'] + stream['ainfo']

def stream_desc(stream):
	return stream['size'] + ' ' + stream['quality'] + ' - ' + stream['size'] + stream['ainfo']

def process_streams(streams):
	listItems = []
	for stream in streams:
		listItem = xbmcgui.ListItem(label=stream_title(stream))
		listItem.setInfo('genre', 'test')
		listItem.addStreamInfo('video', { 'codec': 'h264', 'width' : 1280 })
		listItems.append(listItem)
	return listItems

def add_paging(page, pageCount, nextUrl):
	render_item(build_item(addon.getLocalizedString(30203) + page_info(str(page), pageCount), action[0], nextUrl))
		

def process_seasons(mediaList):
	for i, media in enumerate(mediaList):
		render_item(build_item(media['title'], 'episodes', i), folder = True)

def process_series(mediaList):
	for media in mediaList:
		render_item(build_item(media['title'], 'seasons', '/api/media/series/' + media['id']), folder = True)

def process_episodes(mediaList):
	for i, media in enumerate(mediaList):
		render_item(build_item(media['title'], 'series.streams', action_value[0] + ' ' + str(i)), folder = False)

def process_movies(mediaList):
	for media in mediaList:
		render_item(build_item(media['title'], 'movies.streams', media['id']), folder = False)

def play_video(video_url):
    listItem = xbmcgui.ListItem(path=video_url)
    xbmc.Player().play(item=video_url, listitem=listItem)

def show_stream_dialog(streams):
	dialog = xbmcgui.Dialog()
	index = dialog.select(addon.getLocalizedString(30250), process_streams(streams), useDetails=False)
	if index > -1:
		streamUrl = get_stream_url(str(streams[index]['ident']))
		play_video(streamUrl)

menu = {
	'root': [
		build_item(addon.getLocalizedString(30200), 'folder','movies'),
		build_item(addon.getLocalizedString(30201), 'folder', 'series'),
	],
	'movies': [
		build_item(addon.getLocalizedString(30204), 'search', 'movies'),
		#build_item(addon.getLocalizedString(30211), 'folder','popular'),
		#build_item(addon.getLocalizedString(30212), 'folder','watching now'),
		#build_item(addon.getLocalizedString(30205), 'folder','genre'),
		build_item(addon.getLocalizedString(30206), 'folder','movies.a-z'),
	],
	'series': [
		build_item(addon.getLocalizedString(30204), 'search', 'series'),
		#build_item(addon.getLocalizedString(30211), 'folder','popular'),
		#build_item(addon.getLocalizedString(30212), 'folder','watching now'),
		#build_item(addon.getLocalizedString(30205), 'folder','genre'),
		build_item(addon.getLocalizedString(30206), 'folder','series.a-z'),
	],
	'series.a-z': [build_item('0-9', 'series', '/api/media/series/filter/startsWithL/0-9')] + [build_item(c, 'series', '/api/media/series/filter/startsWithL/' + c) for c in ascii_uppercase],
	'movies.a-z': [build_item('0-9', 'movies', '/api/media/movies/filter/startsWithL/0-9')] + [build_item(c, 'movies', '/api/media/movies/filter/startsWithL/' + c) for c in ascii_uppercase]
}


action = args.get('action', None)
action_value = args.get('action_value', None)
if action is None:
	for c in menu['root']:
		render_item(c)
elif action[0] == 'folder':
	for c in menu[action_value[0]]:
		render_item(c)
elif action[0] == 'movies':
	data = get_media_data(action_value[0])
	process_movies(data['data'])
	if 'next' in data:
		add_paging(data['page'], data['pageCount'], data['next'])
	render_item(build_item(addon.getLocalizedString(30202), ''))
elif action[0] == 'series':
	data = get_media_data(action_value[0])
	process_series(data['data'])
	if 'next' in data:
		add_paging(data['page'], data['pageCount'], data['next'])
	render_item(build_item(addon.getLocalizedString(30202), ''))
elif action[0] == 'series.streams':
	media = get_cache('media')
	s_e = action_value[0].split()
	show_stream_dialog(media['seasons'][int(s_e[0])]['episodes'][int(s_e[1])]['strms'])
elif action[0] == 'movies.streams':
	media = get_media_from_cache(action_value[0])
	show_stream_dialog(media['streams'])
elif action[0] == 'search':
	dialog = xbmcgui.Dialog()
	searchValue = dialog.input(addon.getLocalizedString(30207), defaultt=addon.getLocalizedString(30208), type=xbmcgui.INPUT_ALPHANUM)
	url = '/api/media/' + action_value[0] + '/filter/titleOrActor/' + searchValue
	if action_value[0] == 'movies':
		media = get_media_data(url)
		process_movies(media['data'])
	if action_value[0] == 'series':
		media = api_request(url)
		process_series(media['data'])
	if 'next' in media:
		add_paging(media['page'], media['pageCount'], media['next'])
elif action[0] == 'episodes':
	media = get_cache('media')
	process_episodes(media['seasons'][int(action_value[0])]['episodes'])
elif action[0] == 'seasons':
	media = get_media_data(action_value[0])
	process_seasons(media['seasons'])

xbmcplugin.endOfDirectory(addon_handle)