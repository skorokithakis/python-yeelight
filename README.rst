===========
Description
===========

.. image:: https://gitlab.com/stavros/python-yeelight/badges/master/build.svg
        :target: https://gitlab.com/stavros/python-yeelight/commits/master

.. image:: https://gitlab.com/stavros/python-yeelight/badges/master/coverage.svg
        :target: https://gitlab.com/stavros/python-yeelight/commits/master

.. image:: https://img.shields.io/pypi/v/yeelight.svg
        :target: https://pypi.python.org/pypi/yeelight

.. image:: https://readthedocs.org/projects/yeelight/badge/?version=stable
         :target: http://yeelight.readthedocs.io/en/stable/?badge=stable
         :alt: Documentation Status

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
    >>> bulb.turn_on()

That's it!

Refer to the rest of `the documentation
<https://yeelight.readthedocs.io/en/stable/>`_ for more details.


License
-------

``yeelight`` is distributed under the BSD license.
