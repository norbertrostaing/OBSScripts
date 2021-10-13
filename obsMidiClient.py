# MIDI !
import rtmidi
from rtmidi.midiutil import open_midiinput

import obspython as obs

def testInput(cmdType, channel, value):
    global midiParams
    scenes = obs.obs_frontend_get_scenes()
    transitions = obs.obs_frontend_get_transitions()
    
    
    if midiParams[0] == cmdType and midiParams[1] == channel:
        transition()
    if midiParams[2] == cmdType and channel >= midiParams[3] and channel < midiParams[3] + len(scenes):
        setPreview(channel - midiParams[3])
    if midiParams[4] == cmdType and channel >= midiParams[5] and channel < midiParams[5] + len(transitions):
        setTransition(channel - midiParams[5])
    if midiParams[6]:
        print(cmdType+"\t"+str(channel)+"\t"+str(value))
    

def noteOn(channel, velocity):
    testInput("Note", channel, velocity)

def controlChange(channel, value):
    testInput("CC", channel, value)

currentMidiPort = "";
midiin = None
midiParams = ["",0,"",0,"",0, False];

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port

    def __call__(self, event, data=None):
        message, deltatime = event
        if message[0] == 144 :
            noteOn(message[1], message[2])
        elif message[0] == 176 :
            controlChange(message[1], message[2])


# defines script description 
def script_description():
    return '''Select preview scenes and trigger transition with a midi controller. '''

# defines user properties
def script_properties():
    props = obs.obs_properties_create()
    devicesList = obs.obs_properties_add_list(props, "midiDevice", "MIDI Device", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    midiIn = rtmidi.MidiIn()
    availablePorts = midiIn.get_ports()
    obs.obs_property_list_add_string(devicesList, "", "")
    for port in availablePorts:    
        obs.obs_property_list_add_string(devicesList, port, port)

    transitionMidiType = obs.obs_properties_add_list(props, "transitionMidiType", "Transition midi type", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(transitionMidiType, "Control Change", "CC")
    obs.obs_property_list_add_string(transitionMidiType, "Note On", "Note")
    
    transitionAddress = obs.obs_properties_add_int(props, "transitionMidiAddress", "Transition Midi Address", 0, 127, 1)
    
    
    scenesMidiType = obs.obs_properties_add_list(props, "scenesMidiType", "Scene set midi type", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(scenesMidiType, "Control Change", "CC")
    obs.obs_property_list_add_string(scenesMidiType, "Note On", "Note")
    
    scenesAddress = obs.obs_properties_add_int(props, "scenesMidiAddress", "First scene midi address", 0, 127, 1)
    
    
    transitionsMidiType = obs.obs_properties_add_list(props, "transitionsMidiType", "Transition set midi type", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(transitionsMidiType, "Control Change", "CC")
    obs.obs_property_list_add_string(transitionsMidiType, "Note On", "Note")

    transitionsAddress = obs.obs_properties_add_int(props, "transitionsMidiAddress", "First transition Midi Address", 0, 127, 1)
    
    obs.obs_properties_add_bool(props, "logMidiInput", "Log MIDI input")
    
    return props

# def script_defaults(settings):

# def script_load(settings):

def script_update(settings):
    global currentMidiPort
    global midiin
    global midiParams
    askedPort = obs.obs_data_get_string(settings, "midiDevice")
    if currentMidiPort != askedPort:
        if currentMidiPort != "":
            midiin.close_port();
            currentMidiPort = ""
        ok = True
        if askedPort != "":
            try:
                midiin, port_name = open_midiinput(askedPort)
                midiin.set_callback(MidiInputHandler(port_name))
            except (EOFError, KeyboardInterrupt):
                print("Meh :/")
                ok = False
            if ok:
                currentMidiPort = askedPort
    midiParams[0] = obs.obs_data_get_string(settings, "transitionMidiType")
    midiParams[1] = obs.obs_data_get_int(settings, "transitionMidiAddress")
    midiParams[2] = obs.obs_data_get_string(settings, "scenesMidiType")
    midiParams[3] = obs.obs_data_get_int(settings, "scenesMidiAddress")
    midiParams[4] = obs.obs_data_get_string(settings, "transitionsMidiType")
    midiParams[5] = obs.obs_data_get_int(settings, "transitionsMidiAddress")
    midiParams[6] = obs.obs_data_get_bool(settings, "logMidiInput")
    

def script_unload():
    global currentMidiPort
    global midiin
    if currentMidiPort != "":
        midiin.close_port();


def setTransition(num):
    transitions = obs.obs_frontend_get_transitions()
    if num < len(transitions) and num >= 0:
        obs.obs_frontend_set_current_transition(transitions[num])
        
def transition(num = -1):
    trans = None
    if num >= 0 :
        setTransition(num)
    trans = obs.obs_frontend_get_current_transition()
    act = obs.obs_frontend_get_current_scene()
    mode = obs.OBS_TRANSITION_MODE_AUTO
    duration = 0
    dest = obs.obs_frontend_get_current_preview_scene()
    obs.obs_transition_start(trans, mode, duration, dest)
    obs.obs_frontend_set_current_scene(dest)
    obs.obs_frontend_set_current_preview_scene(act)

def setPreview(num):
    scenes = obs.obs_frontend_get_scenes()
    if num < len(scenes) and num >= 0:
        obs.obs_frontend_set_current_preview_scene(scenes[num])
