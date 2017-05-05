__autopilot_extensions__ = []

try:
    from . import hkplugin
    HAS_HOUSEKEEPER_SUPPORT = True
    __autopilot_extensions__.append(hkplugin.RadioCastellonPodcastCommand)

except ImportError:
    HAS_HOUSEKEEPER_SUPPORT = False
