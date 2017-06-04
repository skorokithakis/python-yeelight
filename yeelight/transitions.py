"""Pre-made transitions, for your strobing pleasure."""

from .flow import HSVTransition, RGBTransition,\
                  TemperatureTransition, SleepTransition
from .utils import _clamp
import random


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


def pulse(red, green, blue, duration=250, brightness=100):
    """
    Pulse a single color once (mainly to be used for notifications).

    :param int red: The red color component to pulse (0-255).
    :param int green: The green color component to pulse (0-255).
    :param int blue: The blue color component to pulse (0-255).
    :param int duration: The duration to pulse for, in milliseconds.
    :param int brightness: The brightness to pulse at (1-100).

    :returns: A list of transitions.
    :rtype: list
    """
    red = _clamp(red, 0, 255)
    green = _clamp(green, 0, 255)
    blue = _clamp(blue, 0, 255)

    transitions = [
        RGBTransition(red, green, blue, duration=duration, brightness=brightness),
        RGBTransition(red, green, blue, duration=duration, brightness=1),
    ]
    return transitions


def strobe_color(brightness=100):
    """
    Rapid flashing colors.

    :param int brightness: The brightness of the transition.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        HSVTransition(240, 100, duration=50, brightness=brightness),
        HSVTransition(60,  100, duration=50, brightness=brightness),
        HSVTransition(330, 100, duration=50, brightness=brightness),
        HSVTransition(0,   100, duration=50, brightness=brightness),
        HSVTransition(173, 100, duration=50, brightness=brightness),
        HSVTransition(30,  100, duration=50, brightness=brightness),
    ]
    return transitions


def alarm(duration=250):
    """
    Red alarm; flashing bright red to dark red.

    :param int duration: The duration between hi/lo brightness,in milliseconds.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        HSVTransition(0, 100, duration=duration, brightness=100),
        HSVTransition(0, 100, duration=duration, brightness=60),
    ]
    return transitions


def police(duration=300, brightness=100):
    """
    Color changes from red to blue, like police lights.

    :param int duration: The duration between red and blue, in milliseconds.
    :param int brightness: The brightness of the transition.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        RGBTransition(255, 0, 0, duration=duration, brightness=brightness),
        RGBTransition(0, 0, 255, duration=duration, brightness=brightness),
    ]
    return transitions


def police2(duration=250, brightness=100):
    """
    Color flashes red and then blue, like urgent police lights.

    :param int duration: The duration to fade to next color, in milliseconds.
    :param int brightness: The brightness of the transition.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        RGBTransition(255, 0, 0, brightness=brightness, duration=duration),
        RGBTransition(255, 0, 0, brightness=1, duration=duration),
        RGBTransition(255, 0, 0, brightness=brightness, duration=duration),
        SleepTransition(duration=duration),
        RGBTransition(0, 0, 255, brightness=brightness, duration=duration),
        RGBTransition(0, 0, 255, brightness=1, duration=duration),
        RGBTransition(0, 0, 255, brightness=brightness, duration=duration),
        SleepTransition(duration=duration),
    ]
    return transitions


def lsd(duration=3000, brightness=100):
    """
    Gradual changes to a pleasing, trippy palette.

    :param int brightness: The brightness of the transition.

    :returns: A list of transitions.
    :rtype: list
    """
    hs_values = [(3, 85), (20, 90), (55, 95), (93, 50), (198, 97)]
    return [HSVTransition(hue, saturation, duration=duration, brightness=brightness) for hue, saturation in hs_values]


def christmas(duration=250, brightness=100, sleep=3000):
    """
    Color changes from red to green, like christmas lights.

    :param int duration: The duration between red and green, in milliseconds.
    :param int brightness: The brightness of the transition.
    :param int sleep: The time to sleep between colors, in milliseconds.

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        HSVTransition(0, 100, duration=duration, brightness=brightness),
        SleepTransition(duration=sleep),
        HSVTransition(120, 100, duration=duration, brightness=brightness),
        SleepTransition(duration=sleep),
    ]
    return transitions


def rgb(duration=250, brightness=100, sleep=3000):
    """
    Color changes from red to green to blue.

    :param int duration: The duration to fade to next color, in milliseconds.
    :param int brightness: The brightness of the transition.
    :param int sleep: The time to sleep between colors, in milliseconds

    :returns: A list of transitions.
    :rtype: list
    """
    transitions = [
        HSVTransition(0,   100, duration=duration, brightness=brightness),
        SleepTransition(duration=sleep),
        HSVTransition(120, 100, duration=duration, brightness=brightness),
        SleepTransition(duration=sleep),
        HSVTransition(240, 100, duration=duration, brightness=brightness),
        SleepTransition(duration=sleep),
    ]
    return transitions


def randomloop(duration=750, brightness=100, count=9):
    """
    Color changes between `count` randomly chosen colors.

    :param int duration: The duration to fade to next color, in milliseconds.
    :param int brightness: The brightness of the transition.
    :param int count: The number of random chosen colors in transition.

    :returns: A list of transitions.
    :rtype: list
    """
    count = _clamp(count, 1, 9)
    transitions = [HSVTransition(random.randint(0, 360), 100,
                   duration=duration) for _ in range(count)]
    return transitions


def slowdown(duration=2000, brightness=100, count=8):
    """
    Changes between `count` random chosen colors with increasing transition time.

    :param int duration: The duration to fade to next color, in milliseconds.
    :param int brightness: The brightness of the transition.
    :param int count: The number of random chosen colors in transition.

    :returns: A list of transitions.
    :rtype: list
    """
    count = _clamp(count, 1, 8)
    transitions = [HSVTransition(random.randint(0, 360), 100,
                   duration=(duration * x)) for x in range(1, count + 1)]
    return transitions
