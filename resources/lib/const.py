class FILTER_TYPE:
    TITLE_OR_ACTOR = 'titleOrActor'
    STARTS_WITH_LETTER = 'startsWithL'
    STARTS_WITH = 'startsWith'


class ENDPOINT:
    MEDIA = 'media'
    FILTER = 'filter'


class PROTOCOL:
    PLUGIN = 'plugin'


class REGEX:
    ROUTER_PARAMS = r"<.*?>"


class ROUTE:
    A_TO_Z = '/a_to_z/<collection>'
    SHOW_CACHED_MEDIA = '/show_cached_media/<collection>'
    NEXT_PAGE = '/next_page/<collection>/<url>'
    FILTER = '/filter/<collection>/<filter_type>/<filter_value>'
    SEARCH = '/search/<collection>'
    COMMAND = '/command/<what>'
    MEDIA_MENU = '/media/<collection>'
    MAIN_MENU = '/main_menu'
    SEARCH_RESULT = '/search_result/<collection>/<search_value>'
    SELECT_STREAM = '/select_stream/<media_id>'
    PLAY_STREAM = '/play_stream/<ident>'


class URL:
    API = 'http://localhost:3000/api/'


class COMMAND:
    SEARCH = 'search'
    OPEN_SETTINGS = 'open-settings'


class CACHE:
    MEDIA = 'media'
    EXPIRATION_TIME = 10
    LAST_ROUTE = 'last_route'
    PLUGIN_URL_HISTORY = 'plugin_url_history'
    PLUGIN_URL_HISTORY_LIMIT = 5
    MEDIA_LIST_RENDERER = 'media_list_renderer'


class DOWNLOAD_TYPE:
    VIDEO_STREAM = 'video_stream'
    FILE_DOWNLOAD = 'file_download'


class SETTINGS:
    UUID = 'uuid'
    DEBUG = 'debug'
    PROVIDER_NAME = 'provider.name'
    PROVIDER_USERNAME = 'provider.username'
    PROVIDER_PASSWORD = 'provider.password'
    PROVIDER_TOKEN = 'provider.token'


class STRINGS:
    STREAM_TITLE = '[I]({lang})[/I]  [{quality}]  [B]{size}[/B] - {ainfo}'
