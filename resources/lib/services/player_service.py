from resources.lib.const import STORAGE, SERVICE_EVENT, SERVICE, SETTINGS
from resources.lib.kodilogging import service_logger
from resources.lib.services import Service
from resources.lib.settings import settings
from resources.lib.storage.storage import storage


class PlayerService(Service):
    SERVICE_NAME = SERVICE.PLAYER_SERVICE

    def __init__(self, api):
        self._api = api
        self._event_callbacks = {
            SERVICE_EVENT.PLAYBACK_STARTED: self.media_played,
            SERVICE_EVENT.PLAYBACK_STOPPED: self.media_stopped
        }

    def media_played(self):
        service_logger.debug('Sending API request to increment play count')
        media_id = storage.get(STORAGE.SELECTED_MEDIA_ID)
        if media_id:
            collection = storage.get(STORAGE.COLLECTION)
            uuid = settings[SETTINGS.UUID]
            self._api.media_played(collection, media_id, uuid)

    @staticmethod
    def media_stopped():
        service_logger.debug('Playback stopped. Removing media ID.')
        storage[STORAGE.SELECTED_MEDIA_ID] = None


