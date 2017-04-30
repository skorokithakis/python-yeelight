Working with Flow
=================

"Flow" is a special mode the bulb can be set to, which is basically a list of
transitions to perform in succession. For example, a flow can be a constant
cycling of colors from one to the next, until it is stopped, or it can be
a quick blink of a certain color.


Usage
-----

To create a flow, we need to instantiate a :py:class:`Flow <yeelight.Flow>`
object and add some transitions to it. The :py:class:`Flow <yeelight.Flow>`
object accepts three parameters, a ``count``, which is the number of
*loops* to perform (*NOT* the number of transitions!), an ``action``,
which is what to do at the end of the flow, and ``transitions``, a list of the
transitions themselves.

In the original protocol spec, the ``count`` argument specifies the number of
transitions to perform. For example, if you have 10 transitions, and ``count``
is 5, the bulb will stop transitioning in the middle of your flow and exit. This
is rather counter-intuitive, so the ``yeelight`` library changes this to mean
"number of loops". If you want to loop once, no matter how long your transition
list, just specify 1. 0 means "loop forever".

``action`` can be ``Flow.actions.recover`` to return to the original state after
this flow is stopped (either through the :py:meth:`stop_flow
<yeelight.Bulb.stop_flow>` method or just because the loop has stopped),
``Flow.actions.stay`` to just stay at the last state of the flow, or
``Flow.actions.off`` to turn off afterwards.

``transitions`` is a list of transition instances. There are various transition
classes available, which are detailed in the :ref:`API reference
<flow-objects>`. The bulbs seem to be limited to around nine transitions (any
more will produce an "invalid command" error).

Let's see a few examples.


Simple example
--------------

A simple example is to cycle the color temperature from 1700 to 6500 twice, with
a one-second delay in-between (the examples assume we have a :py:class:`Bulb
<yeelight.Bulb>` instance in ``bulb``), and then return to the previous state::

    from yeelight import *
    transitions = [
        TemperatureTransition(1700, duration=1000),
        SleepTransition(duration=1000),
        TemperatureTransition(6500, duration=1000)
    ]

    flow = Flow(
        count=2,
        action=Flow.actions.recover,
        transitions=transitions
    )

    bulb.start_flow(flow)


Infinite color cycle
--------------------

We can cycle between colors forever like so::

    from yeelight import *
    transitions = [
        RGBTransition(255, 0, 255, duration=1000)
    ]

    flow = Flow(
        count=0,  # Cycle forever.
        transitions=transitions
    )

    bulb.start_flow(flow)

To stop the flow (and return to the previous state, because of the default
``Flow.actions.recover`` ``action``, you can use :py:meth:`stop_flow
<yeelight.Bulb.stop_flow>`::

    bulb.stop_flow()


Quick pulse
-----------

If you want to connect the bulb to a notification system, you can fire off a
quick pulse. For example, to pulse the bulb green twice when there is a WhatsApp
message and return, we can do::

    from yeelight import *
    transitions = [HSVTransition(hue, 100, duration=500)
                   for hue in range(0, 359, 40)]

    flow = Flow(
        count=2,
        transitions=transitions
    )

    bulb.start_flow(flow)

Pretty easy!


Transition presets
------------------

The library includes some preset transitions in the
:py:mod:`yeelight.transitions` module, to make it easy for you to start.

You can use the transitions simply by calling the preset::

    from yeelight.transitions import *
    from yeelight import Flow

    flow = Flow(
        count=10,
        transitions=disco(),  # Call the transition preset to get the
                              # transitions you like.
    )

    bulb.start_flow(flow)

Remember that the transition presets are functions, so you need to call them.
That's because some of them take parameters.
