from resources.lib.const import STORAGE, SERVICE_EVENT, SERVICE
from resources.lib.kodilogging import service_logger
from resources.lib.services import Service
from resources.lib.storage.storage import storage


class PlayerService(Service):
    SERVICE_NAME = SERVICE.PLAYER_SERVICE

    def __init__(self, api):
        self._api = api
        self._event_callbacks = {
            SERVICE_EVENT.PLAYBACK_STARTED: self.media_played
        }

    def media_played(self):
        service_logger.debug('Sending API request to increment play count')
        media_id = storage.get(STORAGE.SELECTED_MEDIA_ID)
        collection = storage.get(STORAGE.COLLECTION)
        self._api.media_played(collection, media_id)


