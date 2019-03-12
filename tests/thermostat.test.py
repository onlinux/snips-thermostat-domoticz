#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
#
# Import required Python libraries

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys

sys.path.append('..')

from SVT import SVT
from hermes_python.hermes import Hermes
from snipshelpers.config_parser import SnipsConfigParser


CONFIG_INI =  "../config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTAT       = 'ericvde31830:thermostat'
def open_thermostat(config):
    ip = config.get(
        'secret', {
            "ip_domoticz": "192.168.0.160"}).get(
        'ip_domoticz', '192.168.0.160')
    port = config.get(
        'secret', {
            "port": "8080"}).get(
        'port', '8080')

    thermostat = SVT(ip,port)
    return thermostat



def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voila c\'est fait.'
    print(intentName, sentence)

with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
    except :
        config = None

    thermostat = open_thermostat(config)
    print('Thermostat initialization: OK')

    try:
        print("thermostat mode is {}".format(thermostat.mode))
        print("thermostat state is {}".format(thermostat.state))
        print("thermostat pause is {}".format(thermostat.pause))
        # thermostat.mode=10
        # print("thermostat mode is {}".format(thermostat.mode))
        # print("thermostat state is {}".format(thermostat.state))
        # thermostat.state='auto'
        # thermostat.pause=True
        # print("thermostat pause is {}".format(thermostat.pause))
        # print("Indoor temperature is {}°C".format(thermostat.indoorTemp))
        print("Indoor temperature is {}°C".format(thermostat.indoorTemp))
        print("Outdoor temperature is {}°C".format(thermostat.outdoorTemp))

        print("Setpoint normal is {}°C".format(thermostat.setpointNormal))
        print("Setpoint economy  is {}°C".format(thermostat.setpointEconomy))
        thermostat.setpointNormal = 20.9
        thermostat.setpointEconomy = 19.5
    except:
        print("Thermostat error")

    h.subscribe_intents(intent_received).start()
