## SPDX-FileCopyrightText: 2022 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# cedargrove_punk_console.note_in_example.py v1.0

# Tested on an RP2040 Feather using CircuitPython v7.1.1
# Waveform Output pin: A1 (PWM digital output, not analog DAC output)
# Oscillator Frequency Input pin: A2 (analog input)
# One-Shot Multivibrator Pulse Width Input pin: A3 (analog input)

import time
import board
import analogio
import pwmio
from simpleio import map_range
# Note converters: https://github.com/CedarGroveStudios/Unit_Converter
from cedargrove_unit_converter.music_MIDI import note_or_name, note_to_frequency
from cedargrove_punk_console import PunkConsole

# note name, beats
notes = [
    ('C5', 0.25),
    ('E5', 0.25),
    ('G5', 0.25),
    ('C6', 0.25),
    ('B5', 0.25),
    ('G5', 0.25),
    ('F5', 0.25),
    ('D5', 0.25),
]

tempo = 120  # beats-per-minute
tempo_delay = 60 / tempo  # seconds-per-beat

# instantiate a PunkConsole output on pin A1 (PWM-capable)
punk_console_l = PunkConsole(board.A1, mute=True)

# define the potentiometer input for pulse-width
pw_in = analogio.AnalogIn(board.A3)  # One-Shot Pulse Width

i = 0

while True:
    # read the inputs, map to practical audio ranges, send to PunkConsole instance
    #   oscillator frequency determined by note_or_name and note_to_frequency helpers
    #   one-shot pulse width range: 0.5ms to 5ms
    punk_console_l.mute = False

    if i >= len(notes):
        i = 0

    punk_console_l.frequency = note_to_frequency(note_or_name(notes[i][0]))
    punk_console_l.pulse_width_ms = map_range(pw_in.value, 0, 65535, 0.5, 5.0)
    punk_console_l.mute = False

    time.sleep(notes[i][1] * tempo_delay)
    print(i, notes[i][0], punk_console_l.frequency, notes[i][1])
    i += 1
