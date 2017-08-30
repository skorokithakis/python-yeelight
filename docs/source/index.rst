.. image:: _static/yeelight.jpg
   :alt: A YeeLight bulb.
   :align: right

YeeLight library
================

.. image:: https://gitlab.com/stavros/python-yeelight/badges/master/build.svg
         :target: https://gitlab.com/stavros/python-yeelight/commits/master

.. image:: https://gitlab.com/stavros/python-yeelight/badges/master/coverage.svg
         :target: https://gitlab.com/stavros/python-yeelight/commits/master

.. image:: https://img.shields.io/pypi/v/yeelight.svg
         :target: https://pypi.python.org/pypi/yeelight

.. image:: https://readthedocs.org/projects/yeelight/badge/?version=stable
         :target: http://yeelight.readthedocs.io/en/stable/?badge=stable
         :alt: Documentation Status

The YeeLight Python library is a small library that lets you control your
YeeLight RGB LED bulbs over WiFi. The latest version can be found at:

https://gitlab.com/stavros/python-yeelight

To see a real-world usage example, have a look at `yeecli, a command-line
YeeLight utility <https://gitlab.com/stavros/yeecli/>`_ that uses this library.

``yeelight`` currently does not support some features of the `YeeLight API
<http://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf>`_, such as
discovery, but is mostly otherwise complete.


Installation
------------

To install ``yeelight``, you can use ``pip``::

    pip install yeelight

That's all that's required to install the library.


Usage
-----

First of all, you need to discover your bulb's IP. If you already know it, you
can skip to the next section.

Discovering all the devices on your network and their capabilities is easy with
:py:func:`discover_bulbs <yeelight.discover_bulbs>`::

    >>> from yeelight import discover_bulbs
    >>> discover_bulbs()
    [{'capabilities': {'bright': '50',
                       'color_mode': '1',
                       'ct': '2700',
                       'fw_ver': '45',
                       'hue': '359',
                       'id': '0x0000000002dfb19a',
                       'model': 'color',
                       'name': 'bedroom',
                       'power': 'off',
                       'rgb': '16711935',
                       'sat': '100',
                       'support': 'get_prop set_default set_power toggle '
                                  'set_bright start_cf stop_cf set_scene cron_add '
                                  'cron_get cron_del set_ct_abx set_rgb set_hsv '
                                  'set_adjust set_music set_name'},
      'ip': '192.168.0.19',
      'port': 55443},
      {'capabilities': {'bright': '50',
                       'color_mode': '1',
                       'ct': '2700',
                       'fw_ver': '45',
                       'hue': '359',
                       'id': '0x0000000002dfb2f1',
                       'model': 'color',
                       'name': 'livingroom',
                       'power': 'off',
                       'rgb': '16711935',
                       'sat': '100',
                       'support': 'get_prop set_default set_power toggle '
                                  'set_bright start_cf stop_cf set_scene cron_add '
                                  'cron_get cron_del set_ct_abx set_rgb set_hsv '
                                  'set_adjust set_music set_name'},
      'ip': '192.168.0.23',
      'port': 55443}]

That's it, now you know the addresses of all the bulbs on your local network.

Now that you've discovered your bulb's IP, it's time to instantiate a new
:py:class:`Bulb <yeelight.main.Bulb>`::

    >>> from yeelight import Bulb
    >>> bulb = Bulb("192.168.0.19")

    # Turn the bulb on.
    >>> bulb.turn_on()

    # Turn the bulb off.
    >>> bulb.turn_off()

    # Toggle power.
    >>> bulb.toggle()

    # Set brightness to 50%.
    >>> bulb.set_brightness(50)

    # Set RGB value.
    >>> bulb.set_rgb(255, 0, 0)

    # Set HSV value.
    >>> bulb.set_hsv(320, 100, 50)

    # Set hue and saturation, but keep value (brightness) the same.
    >>> bulb.set_hsv(320, 100)

    # Set color temperature.
    >>> bulb.set_color_temp(4700)

    # Save this setting as default.
    >>> bulb.set_default()


For efficiency, ``yeelight`` will use a single TCP connection for all the above
commands. However, this means that, if there's an error, a command could raise
a ``socket.error`` exception and need to be retried. Note that YeeLight
connections are rate-limited to 60 per minute. If you need your connection to
not have a limit, you need to use :py:meth:`Music mode
<yeelight.Bulb.start_music>`.

For a complete list of the commands you can issue, see the :doc:`API reference
<yeelight>`.

By default, ``yeelight`` will refuse to make any changes to the bulb if it's
off::

    >>> bulb.set_brightness(10)
    AssertionError: Commands have no effect when the bulb is off.

You can check the bulb's state by reading its properties::

    >>> bulb.get_properties()
    {'bright': u'10',
     'color_mode': u'2',
     'ct': u'2700',
     'delayoff': u'0',
     'flowing': u'0',
     'hue': u'300',
     'music_on': u'0',
     'name': u'My light',
     'power': u'off',
     'rgb': u'16737280',
     'sat': u'100'}

Notice that the properties don't include `flow_params` by default, as that causes
problems. If you want that, specify it as an argument to `get_properties()`.

If you want to always turn the bulb on before running a command, set ``auto_on``
to ``True``. This will refresh the bulb's properties before most calls, and will
cost you an extra message per command, so watch out for rate-limiting::

    >>> bulb.auto_on = True

    # Or, when instantiating:
    >>> bulb = Bulb("192.168.0.19", auto_on=True)

    # This will work even if the bulb is off.
    >>> bulb.set_brightness(10)

For documentation of the Flow feature, see :doc:`flow`.


Effects
-------

``yeelight`` provides full support for effects. Effects control whether the bulb
changes from one state to the other immediately or gradually, and how long the
gradual change takes.

You can either specify effects to run by default when instantiating, or with
each call::

    >>> bulb = Bulb("192.168.0.19", effect="smooth", duration=1000)

    # This will turn the bulb on gradually within one second:
    >>> bulb.turn_on()

    # This will turn the bulb on immediately:
    >>> bulb.turn_on(effect="sudden")

    # You can easily change the default effect, too:
    >>> bulb.effect = "sudden"

    # This will turn the bulb off immediately:
    >>> bulb.turn_on()


There are two effect types, ``"sudden"`` and ``"smooth"``. The ``"sudden"`` type
ignores the ``duration`` parameter.

Keep in mind that the ``effect`` and ``duration`` parameters *must* be passed by
keyword.


.. toctree::
   :hidden:

   Home <self>
   flow
   API documentation <yeelight>
