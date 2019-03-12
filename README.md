# Snips Smart Virtual Thermostat Domoticz TTS action
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/snipsco/snips-skill-owm/master/LICENSE.txt)

<img class="wp-image-461 size-full" src="/images/thermostat_variables.png" alt=" Zibase Thermostat Variables" />

### Configuration
Enter the local ip address and port of your domoticz server within config.ini

### SAM (preferred)
To install the action on your device, you can use [Sam](https://snips.gitbook.io/getting-started/installation)

`sam install actions -g https://github.com/onlinux/snips-thermostat-domoticz.git`

### Manually

Copy it manually to the device to the folder `/var/lib/snips/skills/`
You'll need `snips-skill-server` installed on the pi

`sudo apt-get install snips-skill-server`

Stop snips-skill-server & generate the virtual environment
```
sudo systemctl stop snips-skill-server
cd /var/lib/snips/skills/snips-thermostat-domoticz/
sh setup.sh
sudo systemctl start snips-skill-server
```

## Logs
Show snips-skill-server logs with sam:

`sam service log snips-skill-server`

Or on the device:

`journalctl -f -u snips-skill-server`

Check general platform logs:

`sam watch`

Or on the device:

`snips-watch`
