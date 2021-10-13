# MIDI !
import rtmidi
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from math import *
import obspython as obs


currentMidiPort = "";
midiOut = None
midiParams = [""];

currentSource = None;
currentQuarter = 0;

updateTimer = None
lastTimeSent = -1

# defines script description 
def script_load(settings):
    global updateTimer
    # updateTimer = obs.timer_add(test, 25)

def script_description():
    return '''Send MTC based on your video file '''

# defines user properties
def script_properties():
    props = obs.obs_properties_create()

    midiOut = rtmidi.MidiOut()
    availablePorts = midiOut.get_ports()

    devicesList = obs.obs_properties_add_list(props, "midiDevice", "MIDI Device", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(devicesList, "", "")
    for port in availablePorts:    
        obs.obs_property_list_add_string(devicesList, port, port)

    sources = obs.obs_enum_sources()
    
    targetSource = obs.obs_properties_add_list(props, "targetSource", "Set Video Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(targetSource, "", "")
    for source in sources:
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(targetSource, name, name);

    return props

# def script_defaults(settings):

# def script_load(settings):

def script_update(settings):
    global currentMidiPort
    global currentSource
    global midiOut
    global midiParams
    askedPort = obs.obs_data_get_string(settings, "midiDevice")
    if currentMidiPort != askedPort:
        if currentMidiPort != "":
            midiOut.close_port();
            currentMidiPort = ""
        ok = True
        if askedPort != "":
            try:
                midiOut, port_name = open_midioutput(askedPort)
            except (EOFError, KeyboardInterrupt):
                print("Meh :/")
                ok = False
            if ok:
                currentMidiPort = askedPort
            else:
                midiOut = None
        else: 
            midiOut = None


    currentSource = obs.obs_data_get_string(settings, "targetSource")

    midiParams[0] = obs.obs_data_get_int(settings, "scenesMidiAddress")
    

def script_unload():
    global currentMidiPort
    global updateTimer
    if currentMidiPort != "":
        midiOut.close_port();
    obs.timer_remove(updateTimer)


quarterFrame = 0;

def sendMTC(h,m,s,f):
    global currentSource
    message = [0xF0, 0x7F, 0x7F, 0x01, 0x01, 96+h, m, s, f, 0xF7]
    # midiOut.send_message(message)

def script_tick(seconds):
    global quarterFrame
    sendAllQuarter()


def sendAllQuarter():
    global midiOut
    global currentSource
    global quarterFrame
    global lastTimeSent
    if midiOut != None and currentSource != "":
        source = obs.obs_get_source_by_name(currentSource)
        if source != None:
            time = obs.obs_source_media_get_time(source)
            if time != lastTimeSent:
                lastTimeSent = time
                ms = time % 1000
                time = floor(time / 1000)
                s = time % 60
                time = floor(time / 60)
                m = time % 60
                time = floor(time / 60)
                h = time
                f = floor(30 * (ms / 1000))
                
                data0 = 0xf1
                data1a = 0
                data1b = currentQuarter << 4

                message = [0xF1, 0]

                data1b = 0 << 4
                data1a = f & 0b00001111
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 1 << 4
                data1a = (f>>4) & 0b00000001
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 2 << 4
                data1a = s & 0b00001111
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 3 << 4
                data1a = (s>>4) & 0b00000011
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 4 << 4
                data1a = m & 0b00001111
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 5 << 4
                data1a = (m>>4) & 0b00000011
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 6 << 4
                data1a = h & 0b00001111
                message[1] = data1a | data1b
                midiOut.send_message(message)

                data1b = 7 << 4
                data1a = (h>>4) & 0b00000001
                data1a = data1a | 0b00000110
                message[1] = data1a | data1b
                midiOut.send_message(message)



def updateQuarter(currentQuarter):
    global midiOut
    global currentSource
    global quarterFrame
    if midiOut != None and currentSource != "":
        source = obs.obs_get_source_by_name(currentSource)
        if source != None:
            time = obs.obs_source_media_get_time(source)

            ms = time % 1000
            time = floor(time / 1000)
            s = time % 60
            time = floor(time / 60)
            m = time % 60
            time = floor(time / 60)
            h = time
            f = floor(25 * (ms / 1000))

            data0 = 0xf1
            data1a = 0
            data1b = currentQuarter << 4

            send = False
            if currentQuarter == 0:
                data1a = f & 0b00001111
                send = True
            if currentQuarter == 1:
                data1a = (f>>4) & 0b00000001
                send = True
            if currentQuarter == 2:
                data1a = s & 0b00001111
                send = True
            if currentQuarter == 3:
                data1a = (s>>4) & 0b00000011
                send = True
            if currentQuarter == 4:
                data1a = m & 0b00001111
                send = True
            if currentQuarter == 5:
                data1a = (m>>4) & 0b00000011
                send = True
            if currentQuarter == 6:
                data1a = h & 0b00001111
                send = True
            if currentQuarter == 7:
                data1a = (h>>4) & 0b00000001
                data1a = data1a | 0b00000110
                send = True

            data = data1a | data1b

            message = [0xF1, data]
            if send:
                midiOut.send_message(message)


            currentQuarter = (currentQuarter + 1 ) % 8            

            #sendMTC(h,m,s,f)

