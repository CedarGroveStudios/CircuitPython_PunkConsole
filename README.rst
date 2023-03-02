Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A CircuitPython-based Atari Punk Console emulation helper class based on the
"Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555 Circuits",
Forrest M. Mims III (1984).


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install cedargrove_punkconsole

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import board
    import analogio
    import pwmio
    from simpleio import map_range
    from cedargrove_punkconsole import PunkConsole

    # instantiate a PunkConsole output on pin A1 (PWM-capable)
    punk_console = PunkConsole(board.A1, mute=False)

    # define the two potentiometer inputs
    f_in = analogio.AnalogIn(board.A2)  # Oscillator Frequency
    pw_in = analogio.AnalogIn(board.A3)  # One-Shot Pulse Width

    while True:
        # read the inputs, map to practical audio ranges, send to PunkConsole instance
        #   oscillator frequency range: 3Hz to 3kHz
        #   one-shot pulse width range: 0.5ms to 5ms
        punk_console.frequency = map_range(f_in.value, 0, 65535, 3, 3000)
        punk_console.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)

Documentation
=============
API documentation for this library can be found in `PunkConsole_API <https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/pseudo_readthedocs_cedargrove_punkconsole.pdf>`_.


.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/Stereo_Punk_Console_test.png

The CedarGrove PunkConsole emulates an astable square-wave oscillator and
synchronized non-retriggerable one-shot monostable multivibrator to create
the classic stepped-tone generator sound of the Atari Punk Console. As with
the original circuit, the oscillator frequency and one-shot pulse width are
the input parameters. Instantiation of the Punk Console class will start the
output waveform based on the input parameters and enable the output signal
if `mute=False`. If no input parameters are provided, the output signal
will be disabled regardless of the mute value. Once instantiated, the class
is controlled by the `frequency`, `pulse_width_ms`, and `mute` properties.

This version of the emulator works only with PWM-capable output pins.

Depending on the timer and PWM capabilities of the host MPU board, the
emulator can easily outperform the original analog circuit. Oscillator
frequency is only limited by the MPU's PWM duty cycle and frequency
parameters, which may create output signals well above the practical audio
hearing range. Therefore, it is recommended that one-shot pulse width input
be limited to the range of 0.5ms and 5ms and that the oscillator frequency
input range be between 3Hz and 3kHz -- although experimentation is
encouraged!

The repo contains three examples, a simple single-channel console, an
annoying stereo noisemaker, and a note table driven sequencer. For the first
two examples, input is provided by potentiometers attached to
two analog input pins. The sequencer is controlled by an internal list of
notes that select the oscillator frequency; pulse width is potentiometer
controlled.

- Minimum and maximum input ranges (may be further limited by the MPU):
    - pulse_width: 0.05ms to  5000ms
    - frequency:      1Hz to >4MHz

- Practical input ranges for audio (empirically determined):
    - pulse_width:  0.5ms to 5ms
    - frequency:      3Hz to 3kHz

The CedarGrove Punk Console algorithm uses PWM frequency and duty cycle
parameters to build the output waveform. The PWM output frequency is an
integer multiple of the oscillator frequency input compared to the one-shot
pulse width input:

``pwm_freq = freq_in / (int((pulse_width) * freq_in) + 1)``

The PWM output duty cycle is calculated after the PWM output frequency is
determined. The PWM output duty cycle is the ratio of the one-shot pulse
width and the wavelength of the PWM output frequency:

``pwm_duty_cycle = pulse_width * pwm_freq``


Planned updates:

For non-PWM analog output, use ``audiocore`` with a waveform sample in the
``RawSample`` binary array, similar to the ``simpleio.tone()`` helper. The output
waveform's duty cycle will be adjusted by altering the contents of the array,
perhaps with `ulab` to improve code execution time. The
``audiocore.RawSample.sample_rate`` frequency is expected to be directly
proportional to the original algorithm's PWM frequency output value, calculated
from the ``sample_rate`` divided by the length of the ``audiocore.RawSample`` array
(number of samples).

MIDI control: A version that uses USB and/or UART MIDI is in the queue. Note
that the ``PunkConsole.mute`` property could be used for note-on and note-off.
``note_in_example.py`` shows how muting can be used for individual notes.

CV control: A Eurorack version was discussed, it's just a bit lower on the
to-do list, that's all. But you know, the first two examples use analog inputs
(0 to +3.3 volts) for frequency and pulse width control. Just sayin'.


.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/CG_PunkConsole_04.jpeg

.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/CG_PunkConsole_01.jpeg

.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/CG_PunkConsole_02.jpeg

.. image:: https://github.com/CedarGroveStudios/CircuitPython_PunkConsole/blob/main/media/CG_PunkConsole_03.jpeg


For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_PunkConsole/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
