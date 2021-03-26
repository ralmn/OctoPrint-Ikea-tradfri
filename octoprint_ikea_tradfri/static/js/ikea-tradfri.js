/*
 * View model for OctoPrint-Ikea-tradfri
 *
 * Author: Mathieu "ralmn" HIREL
 * License: AGPLv3
 */
$(function () {
    function IkeaTradfriViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        //self.loginStateViewModel = parameters[0];
        self.settings = parameters[0];

        self.printer = parameters[3];


        self.wizardDevices = ko.observable([]);
        self.wizardError = ko.observable(null);

        self.sidebarInfo = ko.observable({
            shutdownAt: {},
            cooldown_wait: {}
        });

        self.navInfo = ko.observable({
            state: false
        });

        self.reloadRequired = ko.observable(false);


        self.devices = ko.observable([])

        self.deviceIdEdit = ko.observable(-1);

        self.iconClass = function (dev) {
            let info = self.navInfo().state[dev.id()];
            return "fa fa-" + dev.icon() + " state-icon " + (info && info.state ? 'state-on' : 'state-off');
        };


        self.command = function (command_name, payload) {
            let data = payload || {};
            data.command = command_name;
            $.ajax({
                url: API_BASEURL + "plugin/ikea_tradfri",
                type: "POST",
                dataType: "json",
                data: JSON.stringify(data),
                contentType: "application/json; charset=UTF-8"
            }).done(function (data) {
            });
        };

        self.turnOn = function (dev) {
            self.command("turnOn", {dev: ko.toJS(dev)});
        };
        self.turnOff = function (dev) {
            self.command("turnOff", {dev: ko.toJS(dev)});
        };

        self.canDisplayNavbar = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.selected_devices.length > 0;
        };

        self.statusOk = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "ok";
        };

        self.statusNoDevices = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "no_devices";
        };

        self.statusFailConnection = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "fail_connection";
        };

        self.statusWaiting = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "waiting";
        };

        self.statusOk = function () {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "ok";
        };


        self.getWizardDevices = function () {
            return self.wizardDevices;
        }

        self.wizardTryConnect = function () {
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/wizard/tryConnect",
                type: "POST",
                //dataType: "json",
                data: JSON.stringify({
                    securityCode: $('#wizardIkeaTradfriSecurityCode').val(),
                    gateway: $('#wizardIkeaTradfriGateway').val()
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function (data) {
                //console.log('done', data);
                self.wizardDevices(JSON.parse(data));
                //console.log(self.wizardDevices);
                self.wizardError(null);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        };

        self.onDataUpdaterPluginMessage = function (plugin, msg) {
            if (plugin == 'ikea_tradfri') {
                if (msg.type == 'sidebar') {
                    self.onSidebarInfo(msg.payload);
                } else if (msg.type == 'navbar') {
                    self.navInfo(msg.payload);
                }
            }
        }

        self.onStartupComplete = function (event) {
            self.getSideBarInfo();
            self.getNavbarInfo();
            setInterval(self.getNavbarInfo, 60 * 1000);

        }

        self.getSideBarInfo = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/info",
                type: "GET",
                dataType: "json"
            }).done(self.onSidebarInfo);
        };

        self.getNavbarInfo = function(){
           $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/navbar/info",
                type: "GET",
                dataType: "json"
            }).done(self.navInfo);
        };

        self.onSidebarInfo = function (data) {
            //console.log("onSidebarInfo ==>", data)
            self.sidebarInfo(data);
            // console.log("onSidebarInfo <== ", self.sidebarInfo())
        };

        self.sidebarShutdownAt = function (dev) {
            return new Date((self.sidebarInfo().shutdownAt[dev.id()] || 0) * 1000).toLocaleTimeString();
        }

        self.sidebarInfoShutdownPlanned = function (dev) {
            return self.sidebarInfo() && self.sidebarInfo().shutdownAt[dev.id()] != null
        }

        self.sidebarInfoCooldownPlanned = function(dev){
            return self.sidebarInfo() && self.sidebarInfo().cooldown_wait[dev.id()] != null
        }

        self.postponeShutdown = function () {
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/postpone",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    dev: ko.toJS(this)
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function (jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.cancelShutdown = function () {
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/cancelShutdown",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    dev: ko.toJS(this)
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function (jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.shutdownNow = function () {
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/shutdownNow",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    dev: ko.toJS(this)
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function (jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.onBeforeWizardFinish = function () {
            if ($("#wizardIkeaTradfriDevices").val()) {
                $.ajax({
                    url: BASEURL + "plugin/ikea_tradfri/wizard/setOutlet",
                    type: "POST",
                    //dataType: "json",
                    data: JSON.stringify({
                        selected_outlet: $('#wizardIkeaTradfriDevices').val()
                    }),
                    contentType: "application/json; charset=UTF-8"
                });
            }
            return true;
        };

        self.getDevices = function () {
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/devices",
                type: "GET",
                dataType: "json",
                contentType: "application/json; charset=UTF-8"
            }).done((res) => {
                self.devices(res);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when get devices")
            });
        }

        let currentDevice = null;

        self.showDeviceDialogEdit = function (device) {
            currentDevice = device;

            self.getDevices();

            let dialog = $('#ikea_tradfri_device_modal');
            dialog.find('[name="device_name"]').val(device.name());
            dialog.find('[name="device_id"]').val(device.id());
            dialog.find('[name="on_done"]').prop('checked', device.on_done());
            dialog.find('[name="on_failed"]').prop('checked', device.on_failed());
            dialog.find('[name="stop_timer"]').val(device.stop_timer());
            dialog.find('[name="postpone_delay"]').val(device.postpone_delay());
            dialog.find('[name="connection_timer"]').val(device.connection_timer());
            dialog.find('[name="icon"]').val(device.icon());
            dialog.find('[name="nav_icon"]').prop('checked', device.nav_icon());
            dialog.find('[name="nav_name"]').prop('checked', device.nav_name());
            dialog.find('[name="connect_palette2"]').prop('checked', device.connect_palette2 && device.connect_palette2());

            dialog.find('[name="turn_off_mode"]').val(device.turn_off_mode());
            dialog.find('[name="cooldown_bed"]').val(device.cooldown_bed());
            dialog.find('[name="cooldown_hotend"]').val(device.cooldown_hotend());

            self.dialogOnTurnOffModeChange();

            dialog.modal();
            self.deviceIdEdit(device.id());
        }


        self.showDeviceDialogNew = function (device) {
            currentDevice = null;

            self.getDevices();

            let dialog = $('#ikea_tradfri_device_modal');
            dialog.find('[name="device_name"]').val('Unnamed printer');
            dialog.find('[name="device_id"]').val(-1);
            self.deviceIdEdit(-1);
            dialog.find('[name="on_done"]').prop('checked', true);
            dialog.find('[name="on_failed"]').prop('checked', true);
            dialog.find('[name="stop_timer"]').val(30);
            dialog.find('[name="postpone_delay"]').val(60);
            dialog.find('[name="connection_timer"]').val(5);
            dialog.find('[name="icon"]').val('plug');
            dialog.find('[name="nav_icon"]').prop('checked', true);
            dialog.find('[name="nav_name"]').prop('checked', false);
            let connect_palette2 = dialog.find('[name="connect_palette2"]');
            if (connect_palette2)
                connect_palette2.prop('checked', false);

            dialog.find('[name="turn_off_mode"]').val('cooldown');
            dialog.find('[name="cooldown_bed"]').val(-1);
            dialog.find('[name="cooldown_hotend"]').val(50);

            self.dialogOnTurnOffModeChange();

            dialog.modal();
        }

        self.saveDeviceDialog = function () {
            let dialog = $('#ikea_tradfri_device_modal');
            let device = {
                name: dialog.find('[name="device_name"]').val(),
                id: parseInt(dialog.find('[name="device_id"]').val()),
                on_done: dialog.find('[name="on_done"]').prop('checked'),
                on_failed: dialog.find('[name="on_failed"]').prop('checked'),
                stop_timer: parseInt(dialog.find('[name="stop_timer"]').val()),
                postpone_delay: parseInt(dialog.find('[name="postpone_delay"]').val()),
                connection_timer: parseInt(dialog.find('[name="connection_timer"]').val()),
                icon: dialog.find('[name="icon"]').val(),
                nav_icon: dialog.find('[name="nav_icon"]').prop('checked'),
                nav_name: dialog.find('[name="nav_name"]').prop('checked'),
                turn_off_mode: dialog.find('[name="turn_off_mode"]').val(),
                cooldown_bed: dialog.find('[name="cooldown_bed"]').val(),
                cooldown_hotend: dialog.find('[name="cooldown_hotend"]').val()
            };
            let connect_palette2 = dialog.find('[name="connect_palette2"]');
            if (connect_palette2) {
                device.connect_palette2 = connect_palette2.prop('checked');
            }

            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/device/save",
                type: "POST",
                //dataType: "json",
                data: JSON.stringify({
                    device: device
                }),
                contentType: "application/json; charset=UTF-8"
            }).then((data) => {
                let deviceObs = {}
                for (let key in device) {
                    deviceObs[key] = ko.observable(device[key]);
                }
                if (currentDevice) {
                    self.settings.settings.plugins.ikea_tradfri.selected_devices.replace(currentDevice, deviceObs);
                    if (currentDevice.nav_icon() != deviceObs.nav_icon() || currentDevice.nav_name() != deviceObs.nav_name()) {
                        self.reloadRequired(true);
                    }
                } else {
                    self.settings.settings.plugins.ikea_tradfri.selected_devices.push(deviceObs);
                }

            });

            dialog.modal('hide');

        }

        self.dialogOnTurnOffModeChange = function () {
            let dialog = $('#ikea_tradfri_device_modal');
            const timeMode = dialog.find('[name="turn_off_mode"]').val() === "time";

            $('#plugins_ikea_tradfri_grp_cooldown_bed')[timeMode ? 'hide' : 'show'](); // TODO : c'est moche... faudra voir a changer ça
            $('#plugins_ikea_tradfri_grp_cooldown_hotend')[timeMode ? 'hide' : 'show']();
            $('#plugins_ikea_tradfri_grp_stop_timer')[timeMode ? 'show' : 'hide']();
            //$('#plugins_ikea_tradfri_grp_postpone_delay')[timeMode ? 'show' : 'hide']();

        }


        self.deleteDevice = function (device) {
            let deviceId = device.id();

            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/device/delete",
                type: "POST",
                //dataType: "json",
                data: JSON.stringify({
                    device_id: deviceId
                }),
                contentType: "application/json; charset=UTF-8"
            }).then((data) => {
                self.settings.settings.plugins.ikea_tradfri.selected_devices.remove(device)
            });
            return true;
        }

    }


    if (ko.bindingHandlers['let'] == null) {
        ko.bindingHandlers['let'] = {
            init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
                var innerContext = bindingContext.extend(valueAccessor);
                ko.applyBindingsToDescendants(innerContext, element);
                return {controlsDescendantBindings: true};
            }
        }
    }


    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: IkeaTradfriViewModel,
        additionalNames: ["ikeaTradfriViewModel"],
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel", "loginStateViewModel", "wizardViewModel", "printerStateViewModel"],
        // Elements to bind to, e.g. #settings_plugin_ikea-tradfri, #tab_plugin_ikea-tradfri, ...
        elements: [...Array.from($(".navbar_plugin_ikea_tradfri")).map(e => `#${e.id}`), "#settings_plugin_ikea_tradfri", "#wizard_plugin_ikea_tradfri", "#sidebar_plugin_ikea_tradfri"]
    });
});
