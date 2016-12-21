__author__ = 'Lothilius'


import phue
from os import environ
from se_helpers.actions import wait
from bv_authenticate.Authentication import Authentication as auth

hue_ip, hue_token = auth.hue_bridge()
light_bridge = phue.Bridge(hue_ip, username=hue_token)

light_bridge.connect()

print light_bridge.get_api()

# 'on' : True|False , 'bri' : 0-254, 'sat' : 0-254, 'ct': 154-500
# while True:
light_bridge.set_light(1, parameter={"effect": "none"})
light_bridge.set_light(1, parameter={"hue": 25500})
wait(.5)
light_bridge.set_light(1, parameter={"alert": "select"})
wait(.5)
light_bridge.set_light(1, parameter={"alert": "select"})
wait(.5)
light_bridge.set_light(1, parameter={"alert": "select"})

# light_bridge.set_light(1, parameter={"hue": 25500})

light_bridge.set_light(1, parameter={"effect": "colorloop"})

# wait(2)
# light_bridge.set_light(1, parameter={'xy': [0.15, 0.7]})
# wait(2)