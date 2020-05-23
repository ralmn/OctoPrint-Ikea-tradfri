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
import threading
import uuid

userId = str(uuid.uuid1())[:8]


class IkeaTradfriPlugin(
        octoprint.plugin.EventHandlerPlugin,
        octoprint.plugin.SimpleApiPlugin,
        octoprint.plugin.StartupPlugin,
        octoprint.plugin.SettingsPlugin,
        octoprint.plugin.AssetPlugin,
        octoprint.plugin.TemplatePlugin):

    psk = None
    devices = []
    status = 'waiting'
    error_message = '' 


    def auth(self):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])
        coap_path = self._settings.get(["coap_path"])

        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, "15011/9063")
        api = '{} -m post -e {} -u "Client_identity" -k "{}" "{}"' .format(
            coap_path, "'{ \"9090\":\""+userId+"\" }'", security_code, tradfriHub)
        # self._logger.info(api)
        if os.path.exists(coap_path):
            result = os.popen(api)
        else:
            self._logger.error('[-] libcoap: could not find libcoap.\n')
            self.status = 'connection_failled'
            self.error_message = 'libcoap: could not find libcoap'
            self.save_settings()
            return None

        try:
            data = json.loads(result.read().strip('\n'))
            return data['9091']
        except json.decoder.JSONDecodeError as e:
            self._logger.error('Fail to connect')
            self._logger.error(e)
            return None

    def save_settings(self):
        self._settings.set(['status'], self.status)
        self._settings.set(['error_message'], self.error_message)
        self._settings.set(['devices'], self.devices)
        self._settings.save()
        self._logger.info('Settings saved')
        self._logger.info(self._settings.get(['status']))

    def run_gateway_get_request(self, path):
        gateway_ip = self._settings.get(["gateway_ip"])
        coap_path = self._settings.get(["coap_path"])

        if self.psk is None:
            self.psk = self.auth()
        if self.psk is None:
            self.status = 'connection_failled'
            self.save_settings()
            return None

        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, path)
        api = '{} -m get -u "{}" -k "{}" "{}"' .format(coap_path, userId, self.psk,
                                                       tradfriHub)

        if os.path.exists(coap_path):
            result = os.popen(api)
        else:
            self._logger.error('[-] libcoap: could not find libcoap.\n')

        return json.loads(result.read().strip('\n'))

    def run_gateway_put_request(self, path, data):
        gateway_ip = self._settings.get(["gateway_ip"])
        coap_path = self._settings.get(["coap_path"])

        if(self.psk == None):
            self.psk = self.auth()
        if self.psk is None:
            return None
        tradfriHub = 'coaps://{}:5684/{}' .format(gateway_ip, path)
        api = '{} -m put -e \'{}\' -u "{}" -k "{}" "{}" 2>/dev/null' .format(
            coap_path, data, userId, self.psk, tradfriHub)
        # self._logger.info(api)
        if os.path.exists(coap_path):
            result = os.popen(api)
        else:
            self._logger.error('[-] libcoap: could not find libcoap.\n')

        return True

    def loadDevices(self, startup=False):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])
        if gateway_ip != "" and security_code != "":
            self._logger.info('load devices')
            devices = self.run_gateway_get_request('15001')
            if devices is None:
                return
            self.devices = []
            for i in range(len(devices)):
                # self._logger.info(devices[i])
                dev = self.run_gateway_get_request(
                    '15001/{}'.format(devices[i]))
                # self._logger.info(dev);
                if '3312' in dev:
                    self.devices.append(dict(id=devices[i], name=dev['9001']))
            if len(self.devices):
                self.status = 'ok'
            else:
                self.status = 'no_devices'
        else:
            self._logger.info("No security code or gateway ip")
        self.save_settings()

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.loadDevices()

    def on_after_startup(self):
        self.loadDevices(startup=True)

    # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
            security_code="",
            gateway_ip="",
            psk="",
            selected_outlet=None,
            status='',
            error_message='',
            devices=[],
            on_done=True,
            on_failed=True,
            connection_timer=5,
            stop_timer=30,
            coap_path='/usr/local/bin/coap-client'
        )

    # ~~ TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=True, classes=["dropdown"]),
            dict(type="settings", custom_bindings=True)
        ]

    def get_template_vars(self):
        return dict(
            devices=self.devices,
            status=self.status
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
                pip="https://github.com/ralmn/OctoPrint-Ikea-tradfri/archive/{target_version}.zip"
            )
        )

    def on_event(self, event, payload):
        if event == 'PrintDone' and self._settings.get_boolean(['on_done']):
            stop_timer=int( self._settings.get(['stop_timer']) )
            if stop_timer >= -1:
                c = threading.Timer(stop_timer,self.turnOff)
                c.start()
            else:
                self.turnOff()
        if event == 'PrintFailed' and self._settings.get_boolean(['on_failed']):
            stop_timer=int( self._settings.get(['stop_timer']) )
            if stop_timer >= -1:
                c = threading.Timer(stop_timer,self.turnOff)
                c.start()
            else:
                self.turnOff()
        

    def turnOn(self):
        self.run_gateway_put_request(
            '/15001/{}'.format(self._settings.get(['selected_outlet'])), '{ "3312": [{ "5850": 1 }] }')
        connection_timer=int( self._settings.get(['connection_timer']) )
        if connection_timer >= -1:
            c = threading.Timer(connection_timer,self._printer.connect)
            c.start()

    def turnOff(self):
        self._logger.info('stop')
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
        elif commad == "loadSettings":
            return dict(
                status=self.status,
                devices=self.devices,
                error_message=self.error_message
            )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Ikea-tradfri Plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = IkeaTradfriPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
