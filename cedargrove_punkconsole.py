# SPDX-FileCopyrightText: Copyright (c) 2022 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`cedargrove_punkconsole`
================================================================================

A CircuitPython helper class to emulate the Atari Punk Console.


* Author(s): JG

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

import pwmio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CedarGroveStudios/CircuitPython_PunkConsole.git"


class PunkConsole:
    """A CircuitPython-based Atari Punk Console emulation helper class based on
    the "Stepped Tone Generator" circuit, "Engineer's Mini-Notebook: 555
    Circuits", Forrest M. Mims III (1984).

    The CedarGrove Punk Console emulates an astable square-wave oscillator and
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

    Minimum and maximum input ranges (may be further limited by the MPU):
    pulse_width: 0.05ms to  5000ms
    frequency:      1Hz to >4MHz

    Practical input ranges for audio (empirically determined):
    pulse_width:  0.5ms to 5ms
    frequency:      3Hz to 3kHz

    The CedarGrove Punk Console algorithm uses PWM frequency and duty cycle
    parameters to build the output waveform. The PWM output frequency is an
    integer multiple of the oscillator frequency input compared to the one-shot
    pulse width input:

        `pwm_freq = freq_in / (int((pulse_width) * freq_in) + 1)`

    The PWM output duty cycle is calculated after the PWM output frequency is
    determined. The PWM output duty cycle is the ratio of the one-shot pulse
    width and the wavelength of the PWM output frequency:

        `pwm_duty_cycle = pulse_width * pwm_freq`

    Notes:
    Future update: For non-PWM analog output, the plans are to use audiocore
    with a waveform sample in the `RawSample` binary array, similar to the
    `simpleio.tone()` helper. The output waveform's duty cycle will be adjusted
    by altering the contents of the array, perhaps with `ulab` to improve code
    execution time. The `audiocore.RawSample.sample_rate` frequency is expected
    to be directly proportional to the original algorithm's PWM frequency output
    value, calculated from the `sample_rate` divided by the length of the
    `audiocore.RawSample` array (number of samples).

    MIDI control: A version that uses USB and/or UART MIDI is in the queue. Note
    that the property `PunkConsole.mute` could be used for note-on and note-off.
    `note_in_example.py` shows how muting can be used for individual notes.

    CV control: A Eurorack version was discussed, it's just a bit lower on the
    to-do list, that's all."""

    def __init__(self, pin, frequency=1, pulse_width_ms=0, mute=True):
        """Intantiate and start the oscillator. Initial output is muted by
        default.

        :param ~board pin: The PWM-capable output pin.
        :param int frequency: The oscillator frequency setting in Hertz.
         Defaults to 1 Hertz to squelch output noise.
        :param float pulse_width_ms: The non-retriggerable one-shot monostable
         multivibrator delay (pulse_width) setting in milliseconds. Defaults to
         zero milliseconds to squelch output noise.
        :param bool mute: The output signal state. `True` to mute; `False` to
         unmute. Defaults to muted.
        """

        self._pin = pin
        self._freq_in = frequency
        self._pulse_width_ms = pulse_width_ms
        self._mute = mute

        # Set the maximum PWM frequency and duty cycle values (PWMOut limits)
        # Frequency maximum: 4,294,967,295Hz (32-bits)
        # Duty cycle maximum: 65,535 = 1.0 duty cycle (16-bits)
        self._pwm_freq_range = (2**32) - 1
        self._pwm_duty_cycle_range = (2**16) - 1

        try:
            # Instantiate PWM output with some initial low-noise values
            self._pwm_out = pwmio.PWMOut(self._pin, variable_frequency=True)
            self._pwm_out.frequency = 1
            self._pwm_out.duty_cycle = 0x0000
            self._update()
        except ValueError:
            # The output pin is not PWM capable
            print("Specified output pin is not PWM capable.")

    @property
    def frequency(self):
        """The oscillator frequency integer value setting in Hertz. Defaults to
        1 Hz to squelch output noise."""
        return self._freq_in

    @frequency.setter
    def frequency(self, new_frequency):
        self._freq_in = min(max(new_frequency, 1), self._pwm_freq_range)
        self._lambda_in = 1 / self._freq_in
        self._update()

    @property
    def pulse_width_ms(self):
        """The non-retriggerable one-shot monostable multivibrator delay
        (pulse_width) floating value setting in milliseconds. Defaults to zero
        milliseconds to squelch output noise."""
        return self._pulse_width_ms

    @pulse_width_ms.setter
    def pulse_width_ms(self, new_width):
        self._pulse_width_ms = min(max(new_width, 0.050), 5000)
        self._update()

    @property
    def mute(self):
        """The boolean output signal state: `True` to mute; `False` to unmute
        Defaults to muted."""
        return self._mute

    @mute.setter
    def mute(self, new_mute):
        self._mute = new_mute
        self._update()

    def _update(self):
        """Calculate and set PWM frequency and duty cycle using current
        frequency and pulse width input values."""

        # Set the PWM output frequency based on freq_in and pulse_width_ms
        self._pwm_freq = self._freq_in / (
            int((self._pulse_width_ms / 1000) * self._freq_in) + 1
        )
        self._pwm_out.frequency = int(round(self._pwm_freq, 0))

        # Set the PWM output duty cycle based on pulse_width_ms and pwm_freq
        self._pwm_duty_cycle = (self._pulse_width_ms / 1000) * self._pwm_freq
        if not self._mute:
            self._pwm_out.duty_cycle = int(
                self._pwm_duty_cycle * self._pwm_duty_cycle_range
            )
        else:
            self._pwm_out.duty_cycle = 0
