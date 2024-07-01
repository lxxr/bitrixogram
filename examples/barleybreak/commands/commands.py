# -*- coding: utf-8 -*-
"""
Created on Sun May 19 19:17:24 2024

@author: Aleksey Rublev RCBD.org
"""

import config.settings as config

whook_endpoint = config.ip_whook_endpoint
commands = [
              {'COMMAND': 'move', 'TITLE': 'пятнашки','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint}            
           ]