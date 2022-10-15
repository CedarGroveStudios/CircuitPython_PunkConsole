## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.simple_example.py v1.1

# Tested on an RP2040 Feather using CircuitPython v7.1.1
# Waveform Output pin: A1 (PWM digital output, not analog DAC output)
# Oscillator Frequency Input pin: A2 (analog input)
# One-Shot Multivibrator Pulse Width Input pin: A3 (analog input)

import board
import analogio
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
