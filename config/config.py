# -*- coding: utf-8 -*-
import json

asciiart = """
  ____                  ____             _
 |  _ \ _ __ ___  _ __ |  _ \ ___  _   _| |_ ___     ____
 | | | | '__/ _ \| '_ \| |_) / _ \| | | | __/ _ \   /$#</Digital
 | |_| | | | (_) | |_) |  _ < (_) | |_| | ||  __/  /##*/_Ocean
 |____/|_|  \___/| .__/|_| \_\___/ \__,_|\__\___| /___%#@/
                 |_|                                 /#=/
                                                    /_#/
 ver {ver}                                             /"""

__PULSE_ANIMATION = (
    '[-------]', '[⌃------]', '[⌄^-----]', '[-⌄^----]', '[--⌄^---]',
    '[---⌄^--]', '[----⌄^-]', '[-----⌄^]', '[------⌄]', '[-------]'
)

STATUS_SAMPLEING_INTERVAL = 5
ANIMATION = __PULSE_ANIMATION

#TODO: USe configparser library instead...
FIREWALL_OVPN = json.load(open("config/FIREWALL_OVPN.json", "rb"))
DROPLET_OVPN = json.load(open("config/DROPLET_OVPN.json", "rb"))

with open("config/droproute_deployer.sh", "r") as fh:
    CLOUDINIT_SCRIPT = fh.read()

with open("config/cloudinit.cfg", "r") as fh:
    CLOUDINIT_USERDATA = fh.read()
