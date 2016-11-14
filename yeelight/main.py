import json
import socket

from .decorator import decorator


@decorator
def _command(f, *args, **kw):
    """
    A decorator that wraps a function and enables effects.
    """
    self = args[0]
    effect = kw.get("effect", self.effect)
    duration = kw.get("duration", self.duration)

    if "effect" in kw:
        del kw["effect"]
    if "duration" in kw:
        del kw["duration"]

    method, params = f(*args, **kw)
    if method not in ["toggle", "set_default", "set_name", "cron_add",
                      "cron_get", "cron_del"]:
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

        self.__cmd_id = 0
        self._last_properties = {}
        self.__socket = None

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

        # The bulb will send us updates on its state in addition to responses,
        # so we want to make sure that we read until we see an actual response.
        response = None
        while response is None:
            data = self._socket.recv(16 * 1024)
            lines = [
                json.loads(line.decode("utf8"))
                for line in
                data.split(b"\r\n")
                if line
            ]
            for line in lines:
                if line.get("method") != "props":
                    # This is probably the response we want.
                    response = line
        return response

    @_command
    def set_color_temp(self, degrees):
        """
        Set the bulb's color temperature.

        :param int degrees: The degrees to set the color temperature to
                            (1700-6500).
        """
        self._ensure_on()

        degrees = max(1700, min(6500, degrees))
        return "set_ct_abx", [degrees]

    @_command
    def set_rgb(self, red, green, blue):
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
    def set_hsv(self, hue, saturation):
        """
        Set the bulb's HSV value.

        :param int hue:        The hue to set (0-359).
        :param int saturation: The saturation to set (0-100).
        """
        self._ensure_on()

        hue = max(0, min(359, hue))
        saturation = max(0, min(100, saturation))
        return "set_hsv", [hue, saturation]

    @_command
    def set_brightness(self, brightness):
        """
        Set the bulb's brightness.

        :param int brightness: The brightness value to set (1-100).
        """
        self._ensure_on()

        brightness = max(1, min(100, brightness))
        return "set_bright", [brightness]

    @_command
    def turn_on(self):
        "Turn the bulb on."
        return "set_power", ["on"]

    @_command
    def turn_off(self):
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
    def cron_add(self, event_type, value):
        """
        Add an event to cron.

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
        Add an event to cron.

        :param yeelight.enums.CronType event_type: The type of event. Currently,
                                                   only ``CronType.off``.
        """
        return "cron_del", [event_type.value]
