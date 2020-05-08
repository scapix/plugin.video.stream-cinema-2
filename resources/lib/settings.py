from resources.lib.utils.kodiutils import get_settings, show_settings, set_settings


class Settings:
    def __setitem__(self, key, value):
        set_settings(key, value)

    def __getitem__(self, key):
        return get_settings(key)

    @staticmethod
    def show():
        show_settings()


settings = Settings()
