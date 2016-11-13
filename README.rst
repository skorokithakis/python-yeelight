===========
Description
===========

``yeelight`` is a simple library that allows you to control YeeLight WiFi RGB
LED bulbs through your LAN.


Installation
------------

There are many ways to install ``yeelight``:

* With pip (preferred), do ``pip install yeelight``.
* With setuptools, do ``easy_install yeelight``.
* To install from source, download it from
  https://gitlab.com/stavros/python-yeelight and do
  ``python setup.py install``.


Usage
-----

To use ``yeelight``, just import it in your project like so::

    >>> from yeelight import Bulb

Afterwards, instantiate a bulb::

    >>> bulb = Bulb("192.168.0.5")
    >>> bulb.send_command("set_power", ["off", "smooth", 500])

That's it!

The entire specification for the bulb's protocol is `available online
<http://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf>`_.


License
-------

``yeelight`` is distributed under the BSD license.
