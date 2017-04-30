"""Pre-made transitions, for your strobing pleasure."""

from .flow import HSVTransition, TemperatureTransition


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
