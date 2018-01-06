# -*- coding: utf-8 -*-
import json

asciiart = """  ____                  ____             _
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

HEARTBEAT_INTERVAL = 60
ANIMATION = __PULSE_ANIMATION

FIREWALL_BLOCKING = json.load(open("config/FIREWALL_BLOCKING.json"))
FIREWALL_OVPN = json.load(open("config/FIREWALL_OVPN.json"))
DROPLET_OVPN = json.load(open("config/DROPLET_OVPN.json"))