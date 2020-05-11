from resources.lib.const import STRINGS
from resources.lib.utils.kodiutils import apply_strings


class TextRenderer:
    @staticmethod
    def highlight(text):
        return apply_strings([text], STRINGS.BOLD, STRINGS.COLOR_BLUE)

    @staticmethod
    def bold(text):
        return apply_strings([text], STRINGS.BOLD)

    @staticmethod
    def make_pair(pair_format, text):
        return pair_format.format(*text)

# Cool dialog example
# pairs = [
#         [get_string(LANG.PROVIDER), TextRenderer.highlight(provider.__repr__())],
#         [get_string(LANG.USERNAME), settings[SETTINGS.PROVIDER_USERNAME]],
#         [get_string(LANG.PASSWORD), settings[SETTINGS.PROVIDER_PASSWORD]],
#         [get_string(LANG.TOKEN), settings[SETTINGS.PROVIDER_TOKEN]],
#     ]
#     DialogRenderer.ok_multi_line(get_string(LANG.PROVIDER_DETAILS),
#                                  [TextRenderer.make_pair(STRINGS.PAIR_BOLD, pair) for pair in pairs])
