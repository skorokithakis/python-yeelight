import colorsys
import json
import socket

from .flow import Flow
from .decorator import decorator

MUSIC_PORT = 37657


@decorator
def _command(f, *args, **kw):
    """
    A decorator that wraps a function and enables effects.
    """
    self = args[0]
    effect = kw.get("effect", self.effect)
    duration = kw.get("duration", self.duration)

    method, params = f(*args, **kw)
    if method in ["set_ct_abx", "set_rgb", "set_hsv", "set_bright",
                  "set_power"]:
        # Add the effect parameters.
        params += [effect, duration]

    result = self.send_command(method, params).get("result", [])
    if result:
        return result[0]


class Bulb(object):
    def __init__(self, ip, port=55443, effect="smooth",
                 duration=300, auto_on=False):
        """
        The main controller class of a physical YeeLight bulb.

        :param str ip:       The IP of the bulb.
        :param int port:     The port to connect to on the bulb.
        :param str effect:   The type of effect. Can be "smooth" or "sudden".
        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 30. This is ignored for sudden effects.
        :param bool auto_on: Whether to turn the bulb on automatically before
                             each operation, if it is off.
        """
        self._ip = ip
        self._port = port

        self.effect = effect
        self.duration = duration
        self.auto_on = auto_on

        self.__cmd_id = 0           # The last command id we used.
        self._last_properties = {}  # The last set of properties we've seen.
        self._music_mode = False    # Whether we're currently in music mode.
        self.__socket = None        # The socket we use to communicate.

    @property
    def _cmd_id(self):
        """
        Return the next command ID and increment the counter.

        :rtype: int
        """
        self.__cmd_id += 1
        return self.__cmd_id - 1

    @property
    def _socket(self):
        "Return, optionally creating, the communication socket."
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(5)
            self.__socket.connect((self._ip, self._port))
        return self.__socket

    def _ensure_on(self, auto_on=None):
        """
        Ensure that the bulb is on.

        :param bool auto_on:    If auto_on is True, the bulb is turned on if
                                off before sending a command. If False, an
                                exception will be raised instead.
        :raises AssertionError: if the bulb is off and ``auto_on`` is False.
        """
        if self._music_mode:
            return

        if self._last_properties.get("power") is None:
            self.get_properties()

        if self._last_properties["power"] != "on":
            auto_on = auto_on if auto_on is not None else self.auto_on
            if auto_on:
                self.turn_on()
            else:
                raise AssertionError("Commands have no effect when the bulb is"
                                     " off.")

    def get_properties(self):
        """
        Retrieve the properties of the bulb.

        :returns: A dictionary of param: value items.
        :rtype: dict
        """
        requested_properties = [
            "power", "bright", "ct", "rgb", "hue", "sat",
            "color_mode", "flowing", "delayoff", "flow_params",
            "music_on", "name"
        ]
        response = self.send_command("get_prop", requested_properties)
        properties = response["result"]
        self._last_properties = dict(zip(requested_properties, properties))
        return self._last_properties

    def send_command(self, method, params=None):
        """
        Send a command to the bulb.

        :param str method:  The name of the method to send.
        :param list params: The list of parameters for the method.

        :returns: The response from the bulb.
        """
        command = {
            "id": self._cmd_id,
            "method": method,
            "params": params,
        }

        self._socket.send((json.dumps(command) + "\r\n").encode("utf8"))
        try:
            self._socket.send((json.dumps(command) + "\r\n").encode("utf8"))
        except socket.error:
            # Some error occurred, remove this socket in hopes that we can later
            # create a new one.
            self.__socket.close()
            self.__socket = None
            raise

        if self._music_mode:
            # We're in music mode, nothing else will happen.
            return {"result": ["ok"]}

        # The bulb will send us updates on its state in addition to responses,
        # so we want to make sure that we read until we see an actual response.
        response = None
        while response is None:
            data = self._socket.recv(16 * 1024)
            for line in data.split(b"\r\n"):
                if not line:
                    continue

                try:
                    line = json.loads(line.decode("utf8"))
                except ValueError:
                    line = {"result": ["invalid command"]}

                if line.get("method") != "props":
                    # This is probably the response we want.
                    response = line

        return response

    @_command
    def set_color_temp(self, degrees, **kwargs):
        """
        Set the bulb's color temperature.

        :param int degrees: The degrees to set the color temperature to
                            (1700-6500).
        """
        self._ensure_on()

        degrees = max(1700, min(6500, degrees))
        return "set_ct_abx", [degrees]

    @_command
    def set_rgb(self, red, green, blue, **kwargs):
        """
        Set the bulb's RGB value.

        :param int red: The red value to set (0-255).
        :param int green: The green value to set (0-255).
        :param int blue: The blue value to set (0-255).
        """
        self._ensure_on()

        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))
        return "set_rgb", [red * 65536 + green * 256 + blue]

    @_command
    def set_adjust(self, action, prop):
        """
        Adjust a parameter.

        I don't know what this is good for. I don't know how to use it, or why.
        I'm just including it here for completeness, and because it was easy,
        but it won't get any particular love.

        :param str action: The direction of adjustment. Can be "increase",
                           "decrease" or "circle".
        :param str prop:   The property to adjust. Can be "bright" for
                           brightness, "ct" for color temperature and "color"
                           for color. The only action for "color" can be
                           "circle". Why? Who knows.
        """
        return "set_adjust", [action, prop]

    @_command
    def set_hsv(self, hue, saturation, value=None, **kwargs):
        """
        Set the bulb's HSV value.

        :param int hue:        The hue to set (0-359).
        :param int saturation: The saturation to set (0-100).
        :param int value:      The value to set (0-100). If omitted, the bulb's
                               brightness will remain the same as before the
                               change.
        """
        self._ensure_on()

        # We fake this using flow so we can add the `value` parameter.
        hue = max(0, min(359, hue))
        saturation = max(0, min(100, saturation))

        if value is None:
            # If no value was passed, use ``set_hsv`` to preserve luminance.
            return "set_hsv", [hue, saturation]
        else:
            # Otherwise, use flow.
            value = max(0, min(100, value))

            if kwargs.get("effect", self.effect) == "sudden":
                duration = 50
            else:
                duration = kwargs.get("duration", self.duration)

            hue = max(0, min(359, hue)) / 359.0
            saturation = max(0, min(100, saturation)) / 100.0
            red, green, blue = [int(round(col * 255)) for col in colorsys.hsv_to_rgb(hue, saturation, 1)]
            rgb = red * 65536 + green * 256 + blue
            return "start_cf", [1, 1, "%s, 1, %s, %s" % (duration, rgb, value)]

    @_command
    def set_brightness(self, brightness, **kwargs):
        """
        Set the bulb's brightness.

        :param int brightness: The brightness value to set (1-100).
        """
        self._ensure_on()

        brightness = max(1, min(100, brightness))
        return "set_bright", [brightness]

    @_command
    def turn_on(self, **kwargs):
        "Turn the bulb on."
        return "set_power", ["on"]

    @_command
    def turn_off(self, **kwargs):
        "Turn the bulb off."
        return "set_power", ["off"]

    @_command
    def toggle(self):
        "Toggle the bulb on or off."
        return "toggle", []

    @_command
    def set_default(self):
        "Set the bulb's current state as default."
        return "set_default", []

    @_command
    def set_name(self, name):
        """
        Set the bulb's name.

        :param str name: The string you want to set as the bulb's name.
        """
        return "set_name", [name]

    @_command
    def start_flow(self, flow):
        """
        Start a flow.

        :param yeelight.Flow flow: The Flow instance to start.
        """
        if not isinstance(flow, Flow):
            raise ValueError("Argument is not a Flow instance.")

        self._ensure_on()

        return "start_cf", [flow.count * len(flow.transitions), flow.action.value, flow.expression]

    @_command
    def stop_flow(self):
        """Stop a flow."""
        return "stop_cf", []

    def start_music(self):
        """
        Start music mode.

        Music mode essentially upgrades the existing connection to a reverse one
        (the bulb connects to the library), removing all limits and allowing you
        to send commands without being rate-limited.

        Starting music mode will start a new listening socket, tell the bulb to
        connect to that, and then close the old connection. If the bulb cannot
        connect to the host machine for any reason, bad things will happen (such
        as library freezes).
        """
        if self._music_mode:
            raise AssertionError("Already in music mode, please stop music mode first.")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Reuse sockets so we don't hit "address already in use" errors.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", MUSIC_PORT))
        s.listen(3)

        local_ip = self._socket.getsockname()[0]
        self.send_command("set_music", [1, local_ip, MUSIC_PORT])
        s.settimeout(5)
        conn, _ = s.accept()
        s.close()  # Close the listening socket.
        self.__socket.close()
        self.__socket = conn
        self._music_mode = True

        return "ok"

    @_command
    def stop_music(self):
        """
        Stop music mode.

        Stopping music mode will close the previous connection. Calling
        ``stop_music`` more than once, or while not in music mode, is safe.
        """
        if self.__socket:
            self.__socket.close()
            self.__socket = None
        self._music_mode = False
        return "set_music", [0]

    @_command
    def cron_add(self, event_type, value):
        """
        Add an event to cron.

        Example::

        >>> bulb.cron_add(CronType.off, 10)

        :param yeelight.enums.CronType event_type: The type of event. Currently,
                                                   only ``CronType.off``.
        """
        return "cron_add", [event_type.value, value]

    @_command
    def cron_get(self, event_type):
        """
        Retrieve an event from cron.

        :param yeelight.enums.CronType event_type: The type of event. Currently,
                                                   only ``CronType.off``.
        """
        return "cron_get", [event_type.value]

    @_command
    def cron_del(self, event_type):
        """
        Remove an event from cron.

        :param yeelight.enums.CronType event_type: The type of event. Currently,
                                                   only ``CronType.off``.
        """
        return "cron_del", [event_type.value]
