import json
import socket
from functools import wraps


class Bulb(object):
    def __init__(self, ip, port=55443, effect="smooth",
                 duration=300, auto_on=False):
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
        "Return the next command ID and increment the counter."
        self.__cmd_id += 1
        return self.__cmd_id - 1

    @property
    def _socket(self):
        "Return, optionally creating, the communication socket."
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self._ip, self._port))
        return self.__socket

    def command(func):
        """
        A decorator that wraps a function and enables effects.
        """
        @wraps(func)
        def with_effect(self, *args, **kwargs):
            effect = kwargs.get("effect", self.effect)
            duration = kwargs.get("duration", self.duration)

            if "effect" in kwargs:
                del kwargs["effect"]
            if "duration" in kwargs:
                del kwargs["duration"]

            method, params = func(self, *args, **kwargs)
            if method not in ["toggle", "set_default"]:
                # Add the effect parameters.
                params += [effect, duration]

            self.send_command(method, params)
        return with_effect

    def _ensure_on(self, auto_on=None):
        """
        Ensure that the bulb is on.

        auto_on - If auto_on is True, the bulb is turned on if it is off.
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
        """
        command = {
            "id": self._cmd_id,
            "method": method,
            "params": params,
        }

        self._socket.send(json.dumps(command) + "\r\n")

        # The bulb will send us updates on its state in addition to responses,
        # so we want to make sure that we read until we see an actual response.
        response = None
        while response is None:
            data = self._socket.recv(16 * 1024)
            lines = [json.loads(line) for line in data.split("\r\n") if line]
            for line in lines:
                if line.get("method") == "props":
                    # If we got a notification, update our local state.
                    self._last_properties.update(line["params"])
                else:
                    # Otherwise, it's probably the response we want.
                    response = line
        return response

    @command
    def set_color_temp(self, temperature):
        """
        Set the bulb's color temperature.
        """
        self._ensure_on()

        temperature = max(1700, min(6500, temperature))
        return "set_ct_abx", [temperature]

    @command
    def set_rgb(self, red, green, blue):
        """
        Set the bulb's RGB value.
        """
        self._ensure_on()

        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))
        return "set_rgb", [red * 65536 + green * 256 + blue]

    @command
    def set_hsv(self, hue, saturation):
        """
        Set the bulb's HSV value.
        """
        self._ensure_on()

        hue = max(0, min(359, hue))
        saturation = max(0, min(100, saturation))
        return "set_hsv", [hue, saturation]

    @command
    def set_brightness(self, brightness):
        """
        Set the bulb's brightness.
        """
        self._ensure_on()

        brightness = max(1, min(100, brightness))
        return "set_bright", [brightness]

    @command
    def turn_on(self):
        "Turn the bulb on."
        return "set_power", ["on"]

    @command
    def turn_off(self):
        "Turn the bulb off."
        return "set_power", ["off"]

    @command
    def toggle(self):
        "Toggle the bulb on or off."
        return "toggle", []

    @command
    def set_default(self):
        "Set the bulb's current state as default."
        return "set_default", []
