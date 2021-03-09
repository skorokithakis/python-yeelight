================
python-yeelight
================

Description
------------

``yeelight`` is a simple library that allows you to control YeeLight WiFi RGB
LED bulbs through your LAN.

Forked to support YLTD001-003 lights.


Installation
------------

There are many ways to install ``yeelight``:

* pip3 install git+https://github.com/jess-sys/python-yeelight
* To install from source, download it from
  https://gitlab.com/jess-sys/python-yeelight and do
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
