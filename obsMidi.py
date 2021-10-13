#!/usr/bin/env python
#
# test_midiin_callback.py
#
"""Show how to receive MIDI input by setting a callback function."""

from __future__ import print_function

import logging
import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiinput

midiIn = rtmidi.MidiIn()
availablePorts = midiIn.get_ports()

print(availablePorts)

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        # print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        if message[0] == 144 :
            noteOn(message[1], message[2])
        elif message[0] == 128 :
            noteOff(message[1])
        elif message[0] == 176 :
            noteOff(message[1])

def noteOn(channel, velocity):
    print("noteOn : \t"+str(channel)+"\t"+str(velocity))

def noteOff(channel):
    print("noteOff : \t"+str(channel))

def controlChange(channel, value):
    print("CC : \t" + str(channel) + "\t" + str(value))

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.

try:
    midiin, port_name = open_midiinput(availablePorts[1])
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
del midiin
