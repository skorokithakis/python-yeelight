.. image:: _static/yeelight.jpg
   :alt: A YeeLight bulb.
   :align: right

YeeLight library
================

The YeeLight Python library is a small library that lets you control your
YeeLight RGB LED bulbs over WiFi. The latest version can be found at:

https://gitlab.com/stavros/python-yeelight

There is also `yeecli, a command-line YeeLight utility
<https://gitlab.com/stavros/yeecli/>`_ that uses this library.

``yeelight`` currently does not support some features of the `YeeLight API
<http://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf>`_, such as
discovery or music mode, but is mostly otherwise complete.


Installation
------------

To install ``yeelight``, you can use ``pip``::

    pip install yeelight

That's all that's required to install the library.


Usage
-----

Since ``yeelight`` does not support discovery, you need to discover your bulbs
manually (for example, using ``ping`` or looking at your router's DHCP table).
After you have found your bulb's IP, it's time to instantiate a new
:py:class:`Bulb <yeelight.main.Bulb>`::

    >>> from yeelight import Bulb
    >>> bulb = Bulb("192.168.0.19")

    # Turn the bulb on.
    >>> bulb.turn_on()

    # Turn the bulb off.
    >>> bulb.turn_on()

    # Toggle power.
    >>> bulb.toggle()

    # Set brightness to 50%.
    >>> bulb.set_brightness(50)

    # Set RGB value.
    >>> bulb.set_rgb(255, 0, 0)

    # Set HSV value.
    >>> bulb.set_hsv(320, 100)

    # Set color temperature.
    >>> bulb.set_color_temp(4700)

    # Save this setting as default.
    >>> bulb.set_default()

For a complete list of the commands you can issue, see the :doc:`API reference
<yeelight>`.

By default, ``yeelight`` will refuse to make any changes to the bulb if it's
off::

    >>> bulb.set_brightness(10)
    AssertionError: Commands have no effect when the bulb is off.

You can check the bulb's state by reading its properties::

    >>> bulb.get_properties
    {'bright': u'10',
     'color_mode': u'2',
     'ct': u'2700',
     'delayoff': u'0',
     'flow_params': u'',
     'flowing': u'0',
     'hue': u'300',
     'music_on': u'0',
     'name': u'My light',
     'power': u'off',
     'rgb': u'16737280',
     'sat': u'100'}

If you want to always turn the bulb on before running a command, set ``auto_on``
to ``True``::

    >>> bulb.auto_on = True

    # Or, when instantiating:
    >>> bulb = Bulb("192.168.0.19", auto_on=True)


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
name.


.. toctree::
   :hidden:
   :maxdepth: 2

   Home <self>
   flow
   API documentation <yeelight>
