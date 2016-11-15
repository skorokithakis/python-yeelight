import colorsys
from enum import Enum
from itertools import chain


class Action(Enum):
    """
    The Flow action enumeration.

    Use this as the ``action`` parameter in a flow, to specify what should
    happen after the flow ends.
    """
    recover = 0
    stay = 1
    off = 2


class Flow(object):
    actions = Action

    def __init__(self, count=0, action=Action.recover, transitions=None):
        """
        A complete flow, consisting of one or multiple transitions.

        Example:

        >>> transitions = [RGBTransition(255, 0, 0), SleepTransition(400)]
        >>> Flow(3, Flow.actions.recover, transitions)

        :param int count: The number of times to run this flow (0 to run
                          forever).
        :param action action: The action to take after the flow stops. Can be
                              ``Flow.actions.recover`` to go back to the state
                              before the flow, ``Flow.actions.stay`` to stay at
                              the last state, and ``Flow.actions.off`` to turn
                              off.
        :param list transitions: A list of :py:class:`FlowTransition
                                 <yeelight.FlowTransition>` instances that
                                 describe the flow transitions to perform.
        """
        if transitions is None:
            transitions = []
        self.count = count
        self.action = action
        self.transitions = transitions

    @property
    def expression(self):
        """
        Return a YeeLight-compatible expression that implements this flow.

        :rtype: list
        """
        expr = chain.from_iterable(transition.as_list() for transition in self.transitions)
        expr = ", ".join(str(value) for value in expr)
        return expr


class FlowTransition(object):
    """
    A single transition in the flow.
    """
    def as_list(self):
        """
        Return a YeeLight-compatible expression that implements this transition.

        :rtype: list
        """
        # Duration must be at least 50, otherwise there's an error.
        return [max(50, self.duration), self._mode, self._value, self.brightness]


class RGBTransition(FlowTransition):
    def __init__(self, red, green, blue, duration=300, brightness=100):
        """
        An RGB transition.

        :param int red: The value of red (0-255).
        :param int green: The value of green (0-255).
        :param int blue: The value of blue (0-255).
        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 50.
        :param int brightness: The brightness value to transition to (1-100).
        """
        self.red = red
        self.green = green
        self.blue = blue

        # The mode value the YeeLight protocol mandates.
        self._mode = 1

        self.duration = duration
        self.brightness = brightness

    @property
    def _value(self):
        """The YeeLight-compatible value for this transition."""
        red = max(0, min(255, self.red))
        green = max(0, min(255, self.green))
        blue = max(0, min(255, self.blue))
        return red * 65536 + green * 256 + blue


class HSVTransition(FlowTransition):
    def __init__(self, hue, saturation, duration=300, brightness=100):
        """
        An HSV transition.

        :param int hue: The color hue to transition to (0-359).
        :param int saturation: The color saturation to transition to (0-100).
        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 50.
        :param int brightness: The brightness value to transition to (1-100).
        """
        self.hue = hue
        self.saturation = saturation

        # The mode value the YeeLight protocol mandates.
        self._mode = 1

        self.duration = duration
        self.brightness = brightness

    @property
    def _value(self):
        """The YeeLight-compatible value for this transition."""
        hue = max(0, min(359, self.hue)) / 359.0
        saturation = max(0, min(100, self.saturation)) / 100.0

        red, green, blue = [int(round(col * 255)) for col in colorsys.hsv_to_rgb(hue, saturation, 1)]
        return red * 65536 + green * 256 + blue


class TemperatureTransition(FlowTransition):
    def __init__(self, degrees, duration=300, brightness=100):
        """
        A Color Temperature transition.

        :param int degrees: The degrees to set the color temperature to
                            (1700-6500).
        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 50.
        :param int brightness: The brightness value to transition to (1-100).
        """
        self.degrees = degrees

        # The mode value the YeeLight protocol mandates.
        self._mode = 2

        self.duration = duration
        self.brightness = brightness

    @property
    def _value(self):
        """The YeeLight-compatible value for this transition."""
        return max(1700, min(6500, self.degrees))


class SleepTransition(FlowTransition):
    def __init__(self, duration=300):
        """
        A Sleep transition.

        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 50.
        """
        # The mode value the YeeLight protocol mandates.
        self._mode = 7

        # Ignored by YeeLight.
        self._value = 1
        self.brightness = 2

        self.duration = duration
