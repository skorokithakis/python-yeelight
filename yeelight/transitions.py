"""Pre-made transitions, for your strobing pleasure."""

from .flow import HSVTransition, RGBTransition, TemperatureTransition
from .main import _clamp


def disco(bpm=120):
    """
    Color changes to the beat.

    :param int bpm: The beats per minute to pulse to.

    :returns: A list of transitions.
    :rtype: list
    """
    duration = int(60000 / bpm)
    transitions = [
        HSVTransition(0, 100, duration=duration, brightness=100),
        HSVTransition(0, 100, duration=duration, brightness=1),
        HSVTransition(90, 100, duration=duration, brightness=100),
        HSVTransition(90, 100, duration=duration, brightness=1),
        HSVTransition(180, 100, duration=duration, brightness=100),
        HSVTransition(180, 100, duration=duration, brightness=1),
        HSVTransition(270, 100, duration=duration, brightness=100),
        HSVTransition(270, 100, duration=duration, brightness=1),
    ]
    return transitions


def temp():
    """
    Slowly-changing color temperature.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        TemperatureTransition(1700, duration=40000),
        TemperatureTransition(6500, duration=40000),
    ]
    return transitions


def strobe():
    """
    Rapid flashing on and off.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        HSVTransition(0, 0, duration=50, brightness=100),
        HSVTransition(0, 0, duration=50, brightness=1),
    ]
    return transitions


def pulse(red, green, blue, duration=250):
    """
    Pulse a single color once (mainly to be used for notifications).

    :param int red: The red color component to pulse (0-255).
    :param int green: The green color component to pulse (0-255).
    :param int blue: The blue color component to pulse (0-255).
    :param int duration: The duration to pulse for, in milliseconds.

    :returns: A list of transitions.
    :rtype: list
    """
    red = _clamp(red, 0, 255)
    green = _clamp(green, 0, 255)
    blue = _clamp(blue, 0, 255)

    transitions = [
        RGBTransition(red, green, blue, duration=duration),
        RGBTransition(red, green, blue, duration=duration, brightness=1),
    ]
    return transitions
