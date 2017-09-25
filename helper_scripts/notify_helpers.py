__author__ = 'Lothilius'

from bv_authenticate.Authentication import Authentication as auth
import phue
from se_helpers.actions import wait
import sys
import os


class Notifier(object):
    def __init__(self):
        try:
            self.light_bridge = self.create_light_bridge_object()
            self.specific_light_bulbs = self.get_first_light()
        except:
            pass

    @staticmethod
    def create_light_bridge_object():
        hue_ip, hue_token = auth.hue_bridge()
        light_bridge = phue.Bridge(hue_ip, username=hue_token)

        return light_bridge

    def get_first_light(self):
        first_light = self.light_bridge.get_light_objects(mode='id').keys()[0]
        return first_light

    def alert_the_light(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            wait(.5)
            self.light_bridge.set_light(specific_light_bulbs, parameter={"alert": "select"})
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def set_error_light(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            self.light_bridge.set_light(specific_light_bulbs, parameter={"alert": "select"})
            wait(.5)
            self.light_bridge.set_light(specific_light_bulbs, parameter={"alert": "select"})
            wait(.5)
            self.light_bridge.set_light(specific_light_bulbs, parameter={"hue": 65280})
            wait(.5)
            self.light_bridge.set_light(specific_light_bulbs, parameter={"alert": "lselect"})
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def set_red(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            self.light_bridge.set_light(specific_light_bulbs, parameter={"hue": 0})
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def set_yellow(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            self.light_bridge.set_light(specific_light_bulbs, parameter={"xy": [0.4606, 0.4817]})
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def set_green(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            self.light_bridge.set_light(specific_light_bulbs, parameter={"xy": [.21, .7]})
            wait(.5)
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def set_light_to_normal(self, specific_light_bulbs=None):
        try:
            if specific_light_bulbs is None:
                specific_light_bulbs = self.specific_light_bulbs
            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "none"})
            self.light_bridge.set_light(specific_light_bulbs, parameter={"xy": [.33, .33]})
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def flow_the_light(self, specific_light_bulbs=None):
        try:

            self.light_bridge.set_light(specific_light_bulbs, parameter={"effect": "colorloop"})

        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def wait(self, value):
        wait(value)

    @staticmethod
    def alert_homer():
        try:
            os.system("afplay /Users/martin.valenzuela/Dropbox/Coding/BV/bv_tools/helper_scripts/woohoo.wav")
        except:
            error_result = "Unexpected error 1AH: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


if __name__ == '__main__':
    notify = Notifier()
    notify.flow_the_light(specific_light_bulbs="BizApps backlog")
