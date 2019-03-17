#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
#
# Import required Python libraries
import os
import logging
import logging.config
from hermes_python.hermes import Hermes
from snipshelpers.config_parser import SnipsConfigParser

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys
from SVT import SVT
from SVT import Constants

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

THERMOSTATSHIFT = 'ericvde31830:thermostatShift'
THERMOSTATTURNOFF = 'ericvde31830:thermostatTurnOff'
THERMOSTATMODE = 'ericvde31830:thermostatMode'

# os.path.realpath returns the canonical path of the specified filename,
# eliminating any symbolic links encountered in the path.
path = os.path.dirname(os.path.realpath(sys.argv[0]))
configPath = path + '/' + CONFIG_INI

logging.config.fileConfig(configPath)
logger = logging.getLogger(__name__)


def open_thermostat(config):
    # Set my own lan domoticz server ip address as default
    ip = config.get(
        'global', {
            "ip_domoticz": "192.168.0.160"}).get(
        'ip_domoticz', '192.168.0.160')
    # Set my own  domoticz server port as default : 8080
    port = config.get(
        'global', {
            "port": "8080"}).get(
        'port', '8080')
    # Initialize the all stuff
    thermostat = SVT(ip, port)

    logger.debug(" UrlBase domoticz:{}:{}".format(ip, port))
    logger.debug(" Indoor Temperature:{}°C".format(thermostat.indoorTemp))
    logger.debug(" Outdoor Temperature:{}°C".format(thermostat.outdoorTemp))
    logger.debug(" Thermostat Mode:{}".format(thermostat.mode))
    logger.debug(" Thermostat Pause:{}".format(thermostat.pause))
    logger.debug(" Thermostat State:{}".format(thermostat.state))
    logger.debug(" setpoint Day:  {}°C".format(thermostat.setpointNormal))
    logger.debug(" setpoint Night:{}°C".format(thermostat.setpointEconomy))
    return thermostat


def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    logger.debug(intentName)

    for (slot_value, slot) in intent_message.slots.items():
        logger.debug('Slot {} -> \n\tRaw: {} \tValue: {}'
                     .format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))

    if intentName == THERMOSTATMODE:
        logger.debug("Change thermostat mode")
        if intent_message.slots.thermostat_mode:
            tmode = intent_message.slots.thermostat_mode.first().value
            logger.debug(
                "Je dois passer le thermostat en mode {}".format(tmode))
            sentence = "OK, je passe le thermostat en mode {}".format(tmode)

            # Invert Thermostat.mode dict first
            inv_mode = {value: key for key,
                        value in Constants.mode.items()}
            inv_control = {value: key for key,
                           value in Constants.control.items()}

            if tmode in inv_mode:
                # mode is 'jour' or 'nuit'
                if thermostat.state != 'automatique':
                    thermostat.state = 'automatique'
                logger.debug(inv_mode)
                thermostat.mode = inv_mode[tmode]
            elif tmode in inv_control:
                # 'automatique' or 'forcé' or 'stop'
                logger.debug(inv_control)
                thermostat.state = tmode
            else:
                sentence = 'Désolée mais je ne connais pas le mode {}'.format(
                    tmode)

            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATTURNOFF:
        logger.debug("Thermostat turnOff")
        if intent_message.slots.temperature_device:
            thermostat.state = 'stop'  # Turn economy mode on
            sentence = "Ok, je coupe le thermostat."
            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)
            return

    if intentName == THERMOSTATSHIFT:
        if intent_message.slots.up_down:
            up_down = intent_message.slots.up_down.first().value
            action = up_down

            if action is not None:

                setPoint = None
                mode = thermostat.mode
                state = thermostat.state
                logger.debug("statut: {}, Mode: {}, Action: {}".format(
                    state, mode, action
                ))
                if mode == 'Off':
                    sentence = "Désolée mais nous sommes en mode {}. Je ne fais rien dans ce cas.".format(
                        mode)
                elif action == 'down':
                    if state == 'forcé' or state == 'stop':
                        thermostat.state = 'automatique'

                    elif mode == 'jour':
                        # Need to use the setpoint variable, because domotics takes
                        # a while to update its setpoint
                        setpoint = float(thermostat.setpointNormal) - 0.1
                        thermostat.setpointNormal = setpoint
                        setPoint = str(setpoint).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je descends donc la consigne de jour à {} degrés.".format(
                            mode, setPoint)
                    else:
                        # Need to use the setpoint variable, because domotics takes
                        # a while to update its setpoint
                        setpoint = float(thermostat.setpointEconomy) - 0.1
                        thermostat.setpointEconomy = setpoint
                        setPoint = str(setpoint).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je descends donc la consigne de nuit à {} degrés.".format(
                            mode, setPoint)

                elif action == "up":
                    if 'jour' in mode:
                        # Need to use the setpoint variable, because domotics takes
                        # a while to update its setpoint
                        setpoint = float(thermostat.setpointNormal) + 0.1
                        thermostat.setpointNormal = setpoint
                        setPoint = str(
                            setpoint).replace('.', ',')
                        sentence = "Nous sommes en mode {}, je monte la consigne de jour à {} degrés.".format(
                            mode, setPoint)
                    else:
                        if thermostat.state == 'automatique' and mode == 'nuit':
                            sentence = "Nous sommes en mode économique, je passe donc en mode forcé".format(
                                mode)
                            thermostat.state = 'forcé'

                    logger.debug("After action-> state: {} , mode: {}".format(
                        thermostat.state, thermostat.mode))

                else:
                    sentence = "Je n'ai pas compris s'il fait froid ou s'il fait chaud."

            else:
                sentence = "Je ne comprends pas l'action à effectuer avec le thermostat."

            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)
            return


with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(configPath)

    except BaseException:
        config = None

    thermostat = None

    try:
        thermostat = open_thermostat(config)
        logger.info('Thermostat initialization: OK')

    except Exception as e:
        logger.error('Error Thermostat {}'.format(e))

    h.subscribe_intent(THERMOSTATMODE, intent_received)\
        .subscribe_intent(THERMOSTATTURNOFF, intent_received)\
        .subscribe_intent(THERMOSTATSHIFT, intent_received)\
        .start()
