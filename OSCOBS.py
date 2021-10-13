"""

"""
# osc data

import argparse
import random
import time
import math

from pythonosc import osc_message_builder
from pythonosc import udp_client

#from pythonosc import dispatcher
#from pythonosc import osc_server

targetIp = "127.0.0.1"
targetPort = 8000

client = None
#server = None

#obs !

import obspython as obs
pleaseLog = False

def handleOSC(address, args, data):
    print (address)
    print (args)
    print (data)

# defines script description 
def script_description():
    return '''Send OSC data when source is activated if source name begins with /'''

# defines user properties
def script_properties():
    #global props 
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "host", "Host IP", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "port", "Host port", 1, 400000, 1)
    obs.obs_properties_add_bool(props, "logOscOutput", "Log OSC output")
    # obs.obs_properties_add_int(props, "serverPort", "Listen port", 1, 400000, 1)
    return props

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "host", "127.0.0.1")
    obs.obs_data_set_default_int(settings, "port", 8000)
    # obs.obs_data_set_default_int(settings, "serverPort", 8001)

def source_activated(cd):
    global pleaseLog
    source = obs.calldata_source(cd, "source")
    if source is not None:
        name = obs.obs_source_get_name(source)
        if name[0] == "/":
            client.send_message(name, 1)
            if (pleaseLog):
                print("send " + name)

def script_load(settings):
    global dispatcher
    
    sh = obs.obs_get_signal_handler()
    obs.signal_handler_connect(sh, "source_activate", source_activated)

    # dispatcher = dispatcher.Dispatcher()
    # dispatcher.map("/*", handleOSC)

def script_update(settings):
    global host
    global port
    global client
    global server
    global pleaseLog

    pleaseLog = obs.obs_data_get_bool(settings, "logOscOutput")
    host = obs.obs_data_get_string(settings, "host")
    port = obs.obs_data_get_int(settings, "port")
    client = udp_client.SimpleUDPClient(host, port)
    print("target set to "+host+":"+str(port)+"")

    #serverPort = obs.obs_data_get_int(settings, "serverPort")
    #server = osc_server.ThreadingOSCUDPServer(
    #    ("127.0.0.1", serverPort), dispatcher)
    #print("Serving on {}".format(server.server_address))
