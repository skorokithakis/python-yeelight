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

To use ``yeelight``, first enable "development mode" on your bulb through the YeeLight app.
Then, just import the library into your project like so::

    >>> from yeelight import Bulb

Afterwards, instantiate a bulb::

    >>> bulb = Bulb("192.168.0.5")
    >>> bulb.turn_on()

That's it!

Refer to the rest of `the documentation
<https://yeelight.readthedocs.io/en/stable/>`_ for more details.


Contributing
------------

If you'd like to contribute to the code, thank you! To install the various libraries
required, run (preferably in a virtualenv)::

    $ pip install -Ur requirements_dev.txt

In order for your MR to pass CI, it needs to be checked by various utilities, which are
managed by `pre-commit`. `pre-commit` will be installed by the above command, but you
also need to install the pre-commit hook::

    $ pre-commit install

The hook will run on commit. To run it manually (e.g. if you've already committed but
forgot to run it, just run)::

    $ pre-commit run -a

Thanks again!


License
-------

``yeelight`` is distributed under the BSD license.
