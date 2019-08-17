# coding=utf-8
from __future__ import absolute_import

# (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import octoprint.plugin
import sys
import os
import json

import uuid


global coap
coap = '/usr/local/bin/coap-client'
userId = str(uuid.uuid1())[:8]


class IkeaTradfriPlugin(
        octoprint.plugin.SimpleApiPlugin,
        octoprint.plugin.StartupPlugin,
        octoprint.plugin.SettingsPlugin,
        octoprint.plugin.AssetPlugin,
        octoprint.plugin.TemplatePlugin):

    psk = None
    devices = []

    def auth(self):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])
        
        """ function for getting all tradfri device ids """
        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, "15011/9063")
        self._logger.info(security_code)
        self._logger.info(userId)
        api = '{} -m post -e {} -u "Client_identity" -k "{}" "{}"' .format(
            coap, "'{ \"9090\":\""+userId+"\" }'", security_code, tradfriHub)
        self._logger.info(api)
        if os.path.exists(coap):
            result = os.popen(api)
        else:
            sys.stderr.write('[-] libcoap: could not find libcoap.\n')
            sys.exit(1)

        data = json.loads(result.read().strip('\n'))
        self._logger.info(data)
        return data['9091']

    def run_gateway_get_request(self, path):
        gateway_ip = self._settings.get(["gateway_ip"])
        if(self.psk == None):
            self.psk = self.auth()

        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, path)
        api = '{} -m get -u "{}" -k "{}" "{}"' .format(coap, userId, self.psk,
                                                       tradfriHub)

        if os.path.exists(coap):
            result = os.popen(api)
        else:
            sys.stderr.write('[-] libcoap: could not find libcoap.\n')
            sys.exit(1)

        return json.loads(result.read().strip('\n'))

    def run_gateway_put_request(self, path, data):
        gateway_ip = self._settings.get(["gateway_ip"])
        if(self.psk == None):
            self.psk = self.auth()

        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, path)
        api = '{} -m put -e \'{}\' -u "{}" -k "{}" "{}"' .format(
            coap, data, userId, self.psk, tradfriHub)
        self._logger.info(api)
        if os.path.exists(coap):
            result = os.popen(api)
        else:
            sys.stderr.write('[-] libcoap: could not find libcoap.\n')
            sys.exit(1)

        return

    def loadDevices(self):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])
        if gateway_ip != "" and security_code != "":
            self._logger.info('load devices')
            devices = self.run_gateway_get_request('15001')
            self.devices = []
            for i in range(len(devices)):
                # self._logger.info(devices[i])
                dev = self.run_gateway_get_request(
                    '15001/{}'.format(devices[i]))
                # self._logger.info(dev);
                if '3312' in dev:
                    self.devices.append((devices[i], dev['9001']))

        else:
            self._logger.info("No security code or gateway ip")

    def scan_outlet(self):
        if self.coap_client == None:
            return

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._logger.info(data)
        self.loadDevices()

    def on_after_startup(self):
        self.loadDevices()

    # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
            security_code="",
            gateway_ip="127.0.0.1",
            psk="",
            selected_outlet=-1

        )

    # ~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False, classes=["dropdown"]),
            dict(type="settings", custom_bindings=False)
        ]

    def get_template_vars(self):
        return dict(
            devices=self.devices
        )
    # ~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/ikea-tradfri.js"],
            css=["css/ikea-tradfri.css"],
            less=["less/ikea-tradfri.less"]
        )

    # ~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            ikea_tradfri=dict(
                displayName="Ikea Tradfri Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="ralmn",
                repo="OctoPrint-Ikea-tradfri",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/ralmn/OctoPrint_Ikea-tradfri/archive/{target_version}.zip"
            )
        )

    def turnOn(self):
        self.run_gateway_put_request(
            '/15001/{}'.format(self._settings.get(['selected_outlet'])), '{ "3312": [{ "5850": 1 }] }')

    def turnOff(self):
        self.run_gateway_put_request(
            '/15001/{}'.format(self._settings.get(['selected_outlet'])), '{ "3312": [{ "5850": 0 }] }')

    def get_api_commands(self):
        return dict(
            turnOn=[], turnOff=[]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "turnOn":
            self.turnOn()
        elif command == "turnOff":
            self.turnOff()


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Ikea-tradfri Plugin"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = IkeaTradfriPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
