import colorsys
import json
import logging
import socket

from enum import Enum

from future.utils import raise_from

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .decorator import decorator
from .flow import Flow
from .utils import _clamp

_LOGGER = logging.getLogger(__name__)


@decorator
def _command(f, *args, **kw):
    """A decorator that wraps a function and enables effects."""
    self = args[0]
    effect = kw.get("effect", self.effect)
    duration = kw.get("duration", self.duration)

    method, params = f(*args, **kw)
    if method in ["set_ct_abx", "set_rgb", "set_hsv", "set_bright",
                  "set_power", "toggle"]:
        if self._music_mode:
            # Mapping calls to their properties.
            # Used to keep music mode cache up to date.
            action_property_map = {
                "set_ct_abx": ["ct"],
                "set_rgb": ["rgb"],
                "set_hsv": ["hue", "sat"],
                "set_bright": ["bright"],
                "set_power": ["power"]
            }
            # Handle toggling separately, as it depends on a previous power state.
            if method == "toggle":
                self._last_properties["power"] = "on" if self._last_properties["power"] == "off" else "off"
            elif method in action_property_map:
                set_prop = action_property_map[method]
                update_props = {set_prop[prop]: params[prop] for prop in range(len(set_prop))}
                _LOGGER.debug("Music mode cache update: %s", update_props)
                self._last_properties.update(update_props)
        # Add the effect parameters.
        params += [effect, duration]

    result = self.send_command(method, params).get("result", [])
    if result:
        return result[0]


def discover_bulbs(timeout=2):
    """
    Discover all the bulbs in the local network.

    :param int timeout: How many seconds to wait for replies. Discovery will
                        always take exactly this long to run, as it can't know
                        when all the bulbs have finished responding.

    :returns: A list of dictionaries, containing the ip, port and capabilities
              of each of the bulbs in the network.
    """
    msg = 'M-SEARCH * HTTP/1.1\r\n' \
          'ST:wifi_bulb\r\n' \
          'MAN:"ssdp:discover"\r\n'

    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(timeout)
    s.sendto(msg.encode(), ('239.255.255.250', 1982))

    bulbs = []
    bulb_ips = set()
    while True:
        try:
            data, addr = s.recvfrom(65507)
        except socket.timeout:
            break

        capabilities = dict([x.strip("\r").split(": ") for x in data.decode().split("\n") if ":" in x])
        parsed_url = urlparse(capabilities["Location"])

        bulb_ip = (parsed_url.hostname, parsed_url.port)
        if bulb_ip in bulb_ips:
            continue

        capabilities = {key: value for key, value in capabilities.items() if key.islower()}
        bulbs.append({"ip": bulb_ip[0], "port": bulb_ip[1], "capabilities": capabilities})
        bulb_ips.add(bulb_ip)

    return bulbs


class BulbException(Exception):
    """
    A generic yeelight exception.

    This exception is raised when bulb informs about errors, e.g., when trying
    to issue unsupported commands to the bulb.
    """
    pass


class BulbType(Enum):
    """
    The bulb's type.

    This is either `White` or `Color`, or `Unknown` if the properties have not
    been fetched yet.
    """
    Unknown = -1
    White = 0
    Color = 1


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
        :param bool auto_on: Whether to call :py:meth:`ensure_on()
                             <yeelight.Bulb.ensure_on>` to turn the bulb on
                             automatically before each operation, if it is off.
                             This renews the properties of the bulb before each
                             message, costing you one extra message per command.
                             Turn this off and do your own checking with
                             :py:meth:`get_properties()
                             <yeelight.Bulb.get_properties()>` or run
                             :py:meth:`ensure_on() <yeelight.Bulb.ensure_on>`
                             yourself if you're worried about rate-limiting.
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
        """Return, optionally creating, the communication socket."""
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(5)
            self.__socket.connect((self._ip, self._port))
        return self.__socket

    def ensure_on(self):
        """Turn the bulb on if it is off."""
        if self._music_mode is True or self.auto_on is False:
            return

        self.get_properties()

        if self._last_properties["power"] != "on":
            self.turn_on()

    @property
    def last_properties(self):
        """
        The last properties we've seen the bulb have.

        This might potentially be out of date, as there's no background listener
        for the bulb's notifications. To update it, call
        :py:meth:`get_properties <yeelight.Bulb.get_properties()>`.
        """
        return self._last_properties

    @property
    def bulb_type(self):
        """
        The type of bulb we're communicating with.

        Returns a :py:class:`BulbType <yeelight.BulbType>` describing the bulb
        type. This can either be `Color <yeelight.BulbType.Color>` or
        `White <yeelight.BulbType.White>`.

        When trying to access before properties are known, the bulb type is unknown.

        :rtype: yeelight.BulbType
        :return: The bulb's type.
        """
        if not self._last_properties:
            return BulbType.Unknown
        if not all(name in self.last_properties for name in ['ct', 'rgb', 'hue', 'sat']):
            return BulbType.White
        else:
            return BulbType.Color

    @property
    def music_mode(self):
        """
        Return whether the music mode is active.

        :rtype: bool
        :return: True if music mode is on, False otherwise.
        """
        return self._music_mode

    def get_properties(self):
        """
        Retrieve and return the properties of the bulb.

        This method also updates ``last_properties`` when it is called.

        :returns: A dictionary of param: value items.
        :rtype: dict
        """
        # When we are in music mode, the bulb does not respond to queries
        # therefore we need to keep the state up-to-date ourselves
        if self._music_mode:
            return self._last_properties

        requested_properties = [
            "power", "bright", "ct", "rgb", "hue", "sat",
            "color_mode", "flowing", "delayoff", "flow_params",
            "music_on", "name"
        ]
        response = self.send_command("get_prop", requested_properties)
        properties = response["result"]
        properties = [x if x else None for x in properties]

        self._last_properties = dict(zip(requested_properties, properties))
        return self._last_properties

    def send_command(self, method, params=None):
        """
        Send a command to the bulb.

        :param str method:  The name of the method to send.
        :param list params: The list of parameters for the method.

        :raises BulbException: When the bulb indicates an error condition.
        :returns: The response from the bulb.
        """
        command = {
            "id": self._cmd_id,
            "method": method,
            "params": params,
        }

        _LOGGER.debug("%s > %s", self, command)

        try:
            self._socket.send((json.dumps(command) + "\r\n").encode("utf8"))
        except socket.error as ex:
            # Some error occurred, remove this socket in hopes that we can later
            # create a new one.
            self.__socket.close()
            self.__socket = None
            raise_from(BulbException('A socket error occurred when sending the command.'), ex)

        if self._music_mode:
            # We're in music mode, nothing else will happen.
            return {"result": ["ok"]}

        # The bulb will send us updates on its state in addition to responses,
        # so we want to make sure that we read until we see an actual response.
        response = None
        while response is None:
            try:
                data = self._socket.recv(16 * 1024)
            except socket.error:
                # An error occured, let's close and abort...
                self.__socket.close()
                self.__socket = None
                response = {"error": "Bulb closed the connection."}
                break

            for line in data.split(b"\r\n"):
                if not line:
                    continue

                try:
                    line = json.loads(line.decode("utf8"))
                    _LOGGER.debug("%s < %s", self, line)
                except ValueError:
                    line = {"result": ["invalid command"]}

                if line.get("method") != "props":
                    # This is probably the response we want.
                    response = line
                else:
                    self._last_properties.update(line["params"])

        if "error" in response:
            raise BulbException(response["error"])

        return response

    @_command
    def set_color_temp(self, degrees, **kwargs):
        """
        Set the bulb's color temperature.

        :param int degrees: The degrees to set the color temperature to
                            (1700-6500).
        """
        self.ensure_on()

        degrees = _clamp(degrees, 1700, 6500)
        return "set_ct_abx", [degrees]

    @_command
    def set_rgb(self, red, green, blue, **kwargs):
        """
        Set the bulb's RGB value.

        :param int red: The red value to set (0-255).
        :param int green: The green value to set (0-255).
        :param int blue: The blue value to set (0-255).
        """
        self.ensure_on()

        red = _clamp(red, 0, 255)
        green = _clamp(green, 0, 255)
        blue = _clamp(blue, 0, 255)
        return "set_rgb", [red * 65536 + green * 256 + blue]

    @_command
    def set_adjust(self, action, prop, **kwargs):
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
        self.ensure_on()

        # We fake this using flow so we can add the `value` parameter.
        hue = _clamp(hue, 0, 359)
        saturation = _clamp(saturation, 0, 100)

        if value is None:
            # If no value was passed, use ``set_hsv`` to preserve luminance.
            return "set_hsv", [hue, saturation]
        else:
            # Otherwise, use flow.
            value = _clamp(value, 0, 100)

            if kwargs.get("effect", self.effect) == "sudden":
                duration = 50
            else:
                duration = kwargs.get("duration", self.duration)

            hue = _clamp(hue, 0, 359) / 359.0
            saturation = _clamp(saturation, 0, 100) / 100.0
            red, green, blue = [int(round(col * 255)) for col in colorsys.hsv_to_rgb(hue, saturation, 1)]
            rgb = red * 65536 + green * 256 + blue
            return "start_cf", [1, 1, "%s, 1, %s, %s" % (duration, rgb, value)]

    @_command
    def set_brightness(self, brightness, **kwargs):
        """
        Set the bulb's brightness.

        :param int brightness: The brightness value to set (1-100).
        """
        self.ensure_on()

        brightness = _clamp(brightness, 1, 100)
        return "set_bright", [brightness]

    @_command
    def turn_on(self, **kwargs):
        """Turn the bulb on."""
        return "set_power", ["on"]

    @_command
    def turn_off(self, **kwargs):
        """Turn the bulb off."""
        return "set_power", ["off"]

    @_command
    def toggle(self, **kwargs):
        """Toggle the bulb on or off."""
        return "toggle", []

    @_command
    def set_default(self):
        """Set the bulb's current state as default."""
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

        self.ensure_on()

        return "start_cf", [flow.count * len(flow.transitions), flow.action.value, flow.expression]

    @_command
    def stop_flow(self):
        """Stop a flow."""
        return "stop_cf", []

    def start_music(self, port=0):
        """
        Start music mode.

        Music mode essentially upgrades the existing connection to a reverse one
        (the bulb connects to the library), removing all limits and allowing you
        to send commands without being rate-limited.

        Starting music mode will start a new listening socket, tell the bulb to
        connect to that, and then close the old connection. If the bulb cannot
        connect to the host machine for any reason, bad things will happen (such
        as library freezes).

        :param int port: The port to listen on. If none is specified, a random
                         port will be chosen.
        """
        if self._music_mode:
            raise AssertionError("Already in music mode, please stop music mode first.")

        # Force populating the cache in case we are being called directly
        # without ever fetching properties beforehand
        self.get_properties()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Reuse sockets so we don't hit "address already in use" errors.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        host, port = s.getsockname()
        s.listen(3)

        local_ip = self._socket.getsockname()[0]
        self.send_command("set_music", [1, local_ip, port])
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

    def __repr__(self):
        return "Bulb<{ip}:{port}, type={type}>".format(
            ip=self._ip, port=self._port, type=self.bulb_type)
