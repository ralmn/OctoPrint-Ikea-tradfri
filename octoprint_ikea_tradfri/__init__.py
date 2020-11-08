# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import octoprint.plugin
from octoprint.access import ADMIN_GROUP
from octoprint.access.permissions import Permissions

import sys
import os
import json
import threading
import uuid
import flask
import time
import math
from sarge import capture_stdout
from flask_babel import gettext
from . import cli

userId = str(uuid.uuid1())[:8]


class IkeaTradfriPlugin(
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.WizardPlugin,
    octoprint.plugin.BlueprintPlugin):
    psk = None
    devices = []
    status = 'waiting'
    error_message = ''
    shutdownAt = dict()
    stopTimer = dict()

    def _auth(self, gateway_ip, security_code):
        coap_path = self._settings.get(["coap_path"])

        tradfriHub = 'coaps://{}:5684/{}'.format(gateway_ip, "15011/9063")
        api = '{} -m post -e {} -u "Client_identity" -k "{}" "{}"'.format(
            coap_path, "'{ \"9090\":\"" + userId + "\" }'", security_code, tradfriHub)
        # self._logger.info(api)
        if os.path.exists(coap_path):
            p = capture_stdout(api)
            result = p.stdout.text
            try:
                data = json.loads(result.strip('\n'))
                return data['9091']
            except ValueError as e:
                self._logger.error('Fail to get psk token')
                self._logger.error("stdout: %s" + p.stdout.text)
                self._logger.error("stderr: %s" + p.stderr.text)
                self._logger.error(e)
                return None
        else:
            self._logger.error('[-] libcoap: could not find libcoap.\n')
            self.status = 'connection_failled'
            self.error_message = 'libcoap: could not find libcoap'
            self.save_settings()
            return None

    def auth(self):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])

        return self._auth(gateway_ip, security_code)

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
            self._logger.error('Failed to get psk key (run_gateway_get_request)')
            self.save_settings()
            return None

        tradfriHub = 'coaps://{}:5684/{}'.format(gateway_ip, path)
        api = '{} -m get -u "{}" -k "{}" "{}"'.format(coap_path, userId, self.psk,
                                                      tradfriHub)

        if os.path.exists(coap_path):
            p = capture_stdout(api)
            result = p.stdout.text
        else:
            self._logger.error('[-] libcoap: could not find libcoap.\n')

        return json.loads(result.strip('\n'))

    def run_gateway_put_request(self, path, data):
        gateway_ip = self._settings.get(["gateway_ip"])
        coap_path = self._settings.get(["coap_path"])

        if (self.psk == None):
            self.psk = self.auth()
        if self.psk is None:
            self.status = 'connection_failled'
            self._logger.error('Failed to get psk key (run_gateway_put_request)')
            self.save_settings()
            return None

        tradfriHub = 'coaps://{}:5684/{}'.format(gateway_ip, path)
        api = '{} -m put -e \'{}\' -u "{}" -k "{}" "{}" 2>/dev/null'.format(
            coap_path, data, userId, self.psk, tradfriHub)
        # self._logger.info(api)
        if os.path.exists(coap_path):
            p = capture_stdout(api)
            result = p.stdout.text
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
                if '3312' in dev:  # TODO : Add light
                    self.devices.append(dict(id=devices[i], name=dev['9001'], type="Outlet"))
            if len(self.devices):
                self.status = 'ok'
            else:
                self.status = 'no_devices'
        else:
            self._logger.info("No security code or gateway ip")
        self.save_settings()

    def on_settings_save(self, data):
        # keyAsNumber = ['postponeDelay', 'stop_timer', 'connection_timer']
        # for key in data:
        #     if key in keyAsNumber:
        #         data[key] = int(data[key])

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
            selected_devices=[],
            status='',
            error_message='',
            devices=[],
            coap_path='/usr/local/bin/coap-client',
            config_version_key=1
        )

    # ~~ TemplatePlugin mixin

    def get_template_configs(self):
        configs = [
            dict(type="settings", custom_bindings=True),
            dict(type="wizard", custom_bindings=True),
            dict(type="sidebar", custom_bindings=True)
        ]
        devices = self._settings.get(['selected_devices'])
        for i in range(len(devices)):
            item = dict(
                type="navbar",
                custom_bindings=True,
                suffix="_" + str(devices[i]['id']),
                data_bind="let: {idev: " + str(
                    i) + ", dev: settings.settings.plugins.ikea_tradfri.selected_devices()[" + str(i) + "] }",
                classes=["dropdown navbar_plugin_ikea_tradfri"]
            )
            configs.append(item)

        return configs

    def get_template_vars(self):
        return dict(
            devices=self.devices,
            status=self.status,
            shutdownAt=self.shutdownAt,  # TODO : multi outlet
            postponeDelay=self._settings.get(['postponeDelay'])  # TODO : multi outlet
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

    def navbarInfoData(self):
        # TODO Fix navbar (js/jinja2)
        return dict(
            state=self.getStateData()
        )

    def planStop(self, dev, delay):
        # TODO : multi
        if dev['id'] in self.stopTimer and self.stopTimer[dev['id']] is not None:
            self.stopTimer[dev['id']].cancel()

        now = math.ceil(time.time())

        if self.shutdownAt[dev['id']] is not None:
            self.shutdownAt[dev['id']] += delay
        else:
            self.shutdownAt[dev['id']] = now + delay
        stopIn = (self.shutdownAt[dev['id']] - now)
        self._logger.info("Schedule turn off in %d s" % stopIn)

        def wrapper():
            self.turnOff(dev)

        self.stopTimer[dev['id']] = threading.Timer(stopIn, wrapper)
        self.stopTimer[dev['id']].start()

        self._send_message("sidebar", self.sidebarInfoData())

    def turnOn(self, device):
        if 'type' not in device or device['type'] == 'Outlet':
            self.turnOnOutlet(device['id'])
        else:
            self.turnOnLight(device['id'])

        connection_timer = int(device['connection_timer'])
        if connection_timer >= -1:
            c = threading.Timer(connection_timer, self._printer.connect)
            c.start()
        self._send_message("sidebar", self.sidebarInfoData())
        self._send_message("navbar", self.navbarInfoData())

    def turnOnOutlet(self, deviceId):
        self.run_gateway_put_request(
            '/15001/{}'.format(deviceId), '{ "3312": [{ "5850": 1 }] }')

    def turnOnLight(self, deviceId):
        # TODO
        self._logger.warn("turnOnLight not implemented")
        pass

    def turnOff(self, device):
        self.shutdownAt[device['id']] = None
        if device['id'] in self.stopTimer and self.stopTimer[device['id']] is not None:
            self.stopTimer[device['id']].cancel()
            self.stopTimer[device['id']] = None

        self._send_message("sidebar", self.sidebarInfoData())
        if self._printer.is_printing():
            self._logger.info("Don't turn off outlet because printer is printing !")
            return
        elif self._printer.is_pausing() or self._printer.is_paused():
            self._logger.info("Don't turn off outlet because printer is in pause !")
            return
        elif self._printer.is_cancelling():
            self._logger.info("Don't turn off outlet because printer is cancelling !")
            return

        self._logger.debug('stop')
        if 'type' not in device or device['type'] == 'Outlet':
            self.turnOffOutlet(device['id'])
        else:
            self.turnOffLight(device['id'])
        self._send_message("navbar", self.navbarInfoData())

    def turnOffOutlet(self, deviceId):
        self.run_gateway_put_request('/15001/{}'.format(deviceId), '{ "3312": [{ "5850": 0 }] }')

    def turnOffLight(self, deviceId):
        # TODO
        self._logger.warn("turnOffLight not implemented")
        pass

    def get_api_commands(self):
        return dict(
            turnOn=[], turnOff=[], checkStatus=[]
        )

    def getDeviceFromId(self, id):
        selected_devices = self._settings.get(['selected_devices']);
        device = None
        for dev in selected_devices:
            if dev['id'] == id:
                return dev
        return None

    def on_api_command(self, command, data):
        # TODO : multi outlet
        import flask
        if command == "turnOn":
            if 'dev' in data:
                self.turnOn(data['dev'])
            elif 'ip' in data: # Octopod ?
                device = self.getDeviceFromId(int(data['ip']))
                if device is None:
                    pass
                else:
                    self.turnOn(device)
                    status = self.getStateDataById(device['id'])
                    res = dict(ip=str(device['id']), currentState=("on" if status['state'] else "off"))
                    return flask.jsonify(res)
            else:
                self._logger.warn('turn on without device data')
        elif command == "turnOff":
            if 'dev' in data:
                self.turnOff(data['dev'])
            elif 'ip' in data: # Octopod ?
                device = self.getDeviceFromId(int(data['ip']))
                if device is None:
                    pass
                else:
                    self.turnOff(device)
                    status = self.getStateDataById(device['id'])
                    res = dict(ip=str(device['id']), currentState=("on" if status['state'] else "off"))
                    return flask.jsonify(res)
            else:
                self._logger.warn('turn off without device data')
        elif command == "checkStatus":
            status = None
            if 'dev' in data:
                status = self.getStateDataById(data["dev"]['id'])
                return flask.jsonify(status)
            elif 'ip' in data: # Octopod ?
                device = self.getDeviceFromId(int(data['ip']))
                if device is None:
                    pass
                else:
                    status = self.getStateDataById(device['id'])
                    res = dict(ip=str(device['id']), currentState = ("on" if status['state'] else "off"))
                    return flask.jsonify(res)
            else:
                self._logger.warn('checkStatus without device data')




    def get_additional_permissions(self):
        return [
            dict(key="ADMIN",
                 name="Admin",
                 description=gettext("Allow user to set config."),
                 default_groups=[ADMIN_GROUP],
                 roles=["admins"])
        ]

    @octoprint.plugin.BlueprintPlugin.route("/navbar/info", methods=["GET"])
    def navbarInfo(self):
        data = self.navbarInfoData()
        return flask.make_response(json.dumps(data), 200)

    ##Sidebar

    def sidebarInfoData(self):
        selected_devices = self._settings.get(['selected_devices'])
        for dev in selected_devices:
            if dev['id'] not in self.shutdownAt:
                self.shutdownAt[dev['id']] = None

        return dict(
            shutdownAt=self.shutdownAt
        )

    @octoprint.plugin.BlueprintPlugin.route("/sidebar/info", methods=["GET"])
    def sidebarInfo(self):
        # TODO multi timer
        data = self.sidebarInfoData()
        return flask.make_response(json.dumps(data), 200)

    @octoprint.plugin.BlueprintPlugin.route("/sidebar/postpone", methods=["POST"])
    def sidebarPostponeShutdown(self):
        # TODO multi timer
        dev = flask.request.json['dev']
        postponeDelay = dev['postpone_delay']
        self.planStop(dev, postponeDelay)

        self._send_message("sidebar", self.sidebarInfoData())

        return self.sidebarInfo()

    @octoprint.plugin.BlueprintPlugin.route("/sidebar/cancelShutdown", methods=["POST"])
    def sidebarCancelShutdown(self):
        device = flask.request.json['dev']
        if self.stopTimer[device['id']] is not None:
            self.shutdownAt[device['id']] = None
            self.stopTimer[device['id']].cancel()
            self.stopTimer[device['id']] = None
        self._send_message("sidebar", self.sidebarInfoData())
        return self.sidebarInfo()

    @octoprint.plugin.BlueprintPlugin.route("/sidebar/shutdownNow", methods=["POST"])
    def sidebarShutdownNow(self):
        device = flask.request.json['dev']
        self.turnOff(device)
        self._send_message("sidebar", self.sidebarInfoData())
        return self.sidebarInfo()

    ### Wizard
    def is_wizard_required(self):
        gateway_ip = self._settings.get(["gateway_ip"])
        security_code = self._settings.get(["security_code"])
        selected_devices = self._settings.get(['selected_devices'])
        return gateway_ip == "" or security_code == "" or len(selected_devices) > 0

    def get_wizard_version(self):
        return 1

    @octoprint.plugin.BlueprintPlugin.route("/wizard/coap_path", methods=["POST"])
    def wizardSetCoapPath(self):
        if not "coap_path" in flask.request.json:
            return flask.make_response("Expected coap_path.", 400)
        coap_path = flask.request.json['coap_path']
        self._settings.set(['coap_path'], coap_path)
        self._settings.save()

        return flask.make_response("OK", 200)

    @octoprint.plugin.BlueprintPlugin.route("/wizard/setOutlet", methods=["POST"])
    def wizardSetOutlet(self):
        if not "selected_outlet" in flask.request.json:
            return flask.make_response("Expected selected_outlet.", 400)
        selected_outlet = flask.request.json['selected_outlet']

        # TODO : Handle multiple outlet in wizard

        dev = dict(
            name="Printer",
            id=selected_outlet,
            type="Outlet",
            connection_timer=5,
            stop_timer=30,
            postpone_delay=30,
            on_done=True,
            on_failed=False,
            icon="plug",
            nav_name=False,
            nav_icon=True
        )
        self._settings.set(['selected_devices'], dev)
        self._settings.save()

        return flask.make_response("OK", 200)

    @octoprint.plugin.BlueprintPlugin.route("/wizard/tryConnect", methods=["POST"])
    def wizardTryConnect(self):
        if not "securityCode" in flask.request.json or not "gateway" in flask.request.json:
            return flask.make_response("Expected security code and gateway.", 400)
        securityCode = flask.request.json['securityCode']
        gateway = flask.request.json['gateway']

        if self.psk is not None:
            global userId
            userId = str(uuid.uuid1())[:8]
            self.psk = None

        self.psk = self._auth(gateway, securityCode)

        if self.psk is not None:
            self._settings.set(['security_code'], securityCode)
            self._settings.set(['gateway_ip'], gateway)
            self._settings.save()
            self.loadDevices()

            devices = self._settings.get(['devices'])
            return flask.make_response(json.dumps(devices, indent=4), 200)
        else:
            self._logger.error('Failed to get psk key (wizardTryConnect)')
            return flask.make_response("Failed to connect.", 500)

    @octoprint.plugin.BlueprintPlugin.route("/device/save", methods=["POST"])
    def saveDevice(self):
        if not "device" in flask.request.json:
            return flask.make_response("Missing device", 400)

        device = flask.request.json['device']
        selected_devices = self._settings.get(['selected_devices'])
        index = -1
        for i in range(len(selected_devices)):
            dev = selected_devices[i]
            if dev['id'] == device['id']:
                index = i
                break
        if index >= 0:
            selected_devices[index] = device
        else:
            selected_devices.append(device)

        self._settings.set(['selected_devices'], selected_devices)
        self._settings.save()

        return flask.make_response(json.dumps(selected_devices, indent=4), 200)

    def getStateData(self):
        res = dict()

        selected_devices = self._settings.get(['selected_devices'])
        for device in selected_devices:
            res[device['name']] = self.getStateDataById(device['id'])

        return res

    def getStateDataById(self, device_id):
        data = self.run_gateway_get_request('/15001/{}'.format(device_id))
        state = data["3312"][0]["5850"] == 1

        res = dict(
            state=state
        )
        return res

    def _send_message(self, msg_type, payload):
        self._plugin_manager.send_plugin_message(
            self._identifier,
            dict(type=msg_type, payload=payload))

    def get_settings_version(self):
        return 3

    def on_settings_migrate(self, target, current=None):
        self._logger.info("Update version from {} to {}".format(current, target))
        settings_changed = False

        if current is None or current < 2:
            currentOutletId = self._settings.get(['selected_outlet'])
            stopTimer = self._settings.get(['stop_timer'])
            postponeDelay = self._settings.get(['postponeDelay'])
            connectionTimer = self._settings.get(['connection_timer'])
            on_done = self._settings.get(['on_done'])
            on_failed = self._settings.get(['on_failed'])
            icon = self._settings.get(['icon'])
            devices = [
                dict(
                    name="Printer",
                    id=currentOutletId,
                    type="Outlet",
                    connection_timer=connectionTimer,
                    stop_timer=stopTimer,
                    postpone_delay=postponeDelay,
                    on_done=on_done,
                    on_failed=on_failed,
                    icon=icon,
                    nav_name=False,
                    nav_icon=True
                )
            ]
            self._settings.set(['selected_devices'], devices)
            settings_changed = True

        selected_devices = self._settings.get(['selected_devices'])
        for dev in selected_devices:
            if 'nav_icon' not in dev:
                dev['nav_icon'] = True
                settings_changed = True
            if 'nav_name' not in dev:
                dev['nav_name'] = False
                settings_changed = True
        self._settings.set(['selected_devices'], selected_devices)
        if settings_changed:
            self._settings.save()


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "OctoPrint Ikea Tradfri"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = IkeaTradfriPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.cli.commands": cli.commands,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.access.permissions": __plugin_implementation__.get_additional_permissions
    }
