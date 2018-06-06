from enum import Enum, IntEnum


class CronType(Enum):
    """The type of event in cron."""

    off = 0


class PowerMode(IntEnum):
    """Power mode of the light."""

    LAST = 0
    NORMAL = 1
    RGB = 2
    HSV = 3
    COLOR_FLOW = 4
    MOONLIGHT = 5
