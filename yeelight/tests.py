import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(__file__ + "/../.."))

from yeelight import Bulb  # noqa


class SocketMock(object):
    def __init__(self, received=b'{"id": 0, "result": ["ok"]}'):
        self.received = received

    def send(self, data):
        self.sent = json.loads(data.decode("utf8"))

    def recv(self, length):
        return self.received


class Tests(unittest.TestCase):
    def setUp(self):
        self.socket = SocketMock()
        self.bulb = Bulb(ip="", auto_on=True)
        self.bulb._Bulb__socket = self.socket

    def test_rgb1(self):
        self.bulb.set_rgb(255, 255, 0)
        self.assertEqual(self.socket.sent["method"], "set_rgb")
        self.assertEqual(self.socket.sent["params"], [16776960, 'smooth', 300])

    def test_rgb2(self):
        self.bulb.effect = "sudden"
        self.bulb.set_rgb(255, 255, 0)
        self.assertEqual(self.socket.sent["method"], "set_rgb")
        self.assertEqual(self.socket.sent["params"], [16776960, 'sudden', 300])

    def test_rgb3(self):
        self.bulb.set_rgb(255, 255, 0, effect="sudden")
        self.assertEqual(self.socket.sent["method"], "set_rgb")
        self.assertEqual(self.socket.sent["params"], [16776960, 'sudden', 300])

    def test_hsv1(self):
        self.bulb.set_hsv(200, 100, effect="sudden")
        self.assertEqual(self.socket.sent["method"], "set_hsv")
        self.assertEqual(self.socket.sent["params"], [200, 100, 'sudden', 300])

    def test_hsv2(self):
        self.bulb.set_hsv(200, 100, 10, effect="sudden", duration=500)
        self.assertEqual(self.socket.sent["method"], "start_cf")
        self.assertEqual(self.socket.sent["params"], [1, 1, "50, 1, 43263, 10"])

    def test_hsv3(self):
        self.bulb.set_hsv(200, 100, 10, effect="smooth", duration=1000)
        self.assertEqual(self.socket.sent["method"], "start_cf")
        self.assertEqual(self.socket.sent["params"], [1, 1, "1000, 1, 43263, 10"])

    def test_hsv4(self):
        self.bulb.effect = "sudden"
        self.bulb.set_hsv(200, 100, 10, effect="smooth", duration=1000)
        self.assertEqual(self.socket.sent["method"], "start_cf")
        self.assertEqual(self.socket.sent["params"], [1, 1, "1000, 1, 43263, 10"])

    def test_toggle1(self):
        self.bulb.toggle()
        self.assertEqual(self.socket.sent["method"], "toggle")
        self.assertEqual(self.socket.sent["params"], ["smooth", 300])

        self.bulb.toggle(duration=3000)
        self.assertEqual(self.socket.sent["params"], ["smooth", 3000])

    def test_turn_off1(self):
        self.bulb.turn_off()
        self.assertEqual(self.socket.sent["method"], "set_power")
        self.assertEqual(self.socket.sent["params"], ["off", "smooth", 300])

        self.bulb.turn_off(duration=3000)
        self.assertEqual(self.socket.sent["params"], ["off", "smooth", 3000])

    def test_turn_on1(self):
        self.bulb.turn_on()
        self.assertEqual(self.socket.sent["method"], "set_power")
        self.assertEqual(self.socket.sent["params"], ["on", "smooth", 300])

        self.bulb.turn_on(duration=3000)
        self.assertEqual(self.socket.sent["params"], ["on", "smooth", 3000])

    def test_turn_on2(self):
        self.bulb.effect = "sudden"
        self.bulb.turn_on()
        self.assertEqual(self.socket.sent["method"], "set_power")
        self.assertEqual(self.socket.sent["params"], ["on", "sudden", 300])

    def test_turn_on3(self):
        self.bulb.turn_on(effect="sudden", duration=50)
        self.assertEqual(self.socket.sent["method"], "set_power")
        self.assertEqual(self.socket.sent["params"], ["on", "sudden", 50])

    def test_color_temp1(self):
        self.bulb.set_color_temp(1400)
        self.assertEqual(self.socket.sent["method"], "set_ct_abx")
        self.assertEqual(self.socket.sent["params"], [1700, "smooth", 300])

        self.bulb.set_color_temp(1400, duration=3000)
        self.assertEqual(self.socket.sent["params"], [1700, "smooth", 3000])

    def test_color_temp2(self):
        self.bulb.set_color_temp(8400, effect="sudden")
        self.assertEqual(self.socket.sent["method"], "set_ct_abx")
        self.assertEqual(self.socket.sent["params"], [6500, "sudden", 300])


if __name__ == '__main__':
    unittest.main()
