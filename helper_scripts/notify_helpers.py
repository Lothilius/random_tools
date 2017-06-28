__author__ = 'Lothilius'

from bv_authenticate.Authentication import Authentication as auth
import phue
from se_helpers.actions import wait
import sys
import os



def alert_homer():
    try:
        os.system("afplay /Users/martin.valenzuela/Dropbox/Coding/BV/bv_tools/helper_scripts/woohoo.wav")
    except:
        error_result = "Unexpected error 1AH: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def alert_the_light():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"alert": "select"})
        wait(.5)
        light_bridge.set_light(1, parameter={"alert": "select"})
        wait(.5)
        light_bridge.set_light(1, parameter={"alert": "select"})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def set_error_light():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"alert": "select"})
        wait(.5)
        light_bridge.set_light(1, parameter={"alert": "select"})
        wait(.5)
        light_bridge.set_light(1, parameter={"hue": 65280})
        wait(.5)
        light_bridge.set_light(1, parameter={"alert": "lselect"})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def set_red():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"hue": 0})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def set_yellow():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"xy": [.48, .46]})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def set_green():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"xy": [.21, .7]})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def set_light_to_normal():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)
        light_bridge.set_light(1, parameter={"effect": "none"})
        light_bridge.set_light(1, parameter={"xy": [.33, .33]})
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

def flow_the_light():
    try:
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)

        light_bridge.set_light(1, parameter={"effect": "colorloop"})

    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

if __name__ == '__main__':
    set_light_to_normal()