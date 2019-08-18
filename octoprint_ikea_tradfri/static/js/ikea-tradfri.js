/*
 * View model for OctoPrint-Ikea-tradfri
 *
 * Author: Mathieu "ralmn" HIREL
 * License: AGPLv3
 */
$(function() {
    function IkeaTradfriViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        //self.loginStateViewModel = parameters[0];
        self.settings = parameters[0];

        self.turnOn = function() {
            $.ajax({
                url: API_BASEURL + "plugin/ikea_tradfri",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "turnOn"
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {});
        };
        self.turnOff = function() {
            $.ajax({
                url: API_BASEURL + "plugin/ikea_tradfri",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "turnOff"
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {});
        };

        self.canDisplayNavbar = function() {
            return ![null, "-1", -1, undefined].includes(self.settings.getLocalData().plugins.ikea_tradfri.selected_outlet);
        };

        self.statusOk = function() {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "ok";
        };

        self.statusNoDevices = function() {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "no_devices";
        };

        self.statusFailConnection = function() {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "fail_connection";
        };

        self.statusWaiting = function() {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "waiting";
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: IkeaTradfriViewModel,
        additionalNames: ["ikeaTradfriViewModel"],
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_ikea-tradfri, #tab_plugin_ikea-tradfri, ...
        elements: ["#navbar_plugin_ikea_tradfri", "#settings_plugin_ikea_tradfri"]
    });
});
