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

        self.printer = parameters[3];

        console.log(self.printer);

        self.wizardDevices=ko.observable([]);
        self.wizardError=ko.observable(null);

        self.sidebarInfo = ko.observable({
            shutdownAt: null
        });


        self.iconClass =  ko.pureComputed(function(){
            return "fa fa-" + self.settings.getLocalData().plugins.ikea_tradfri.icon;
        });

        self.command = function(command_name) {
            $.ajax({
                url: API_BASEURL + "plugin/ikea_tradfri",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: command_name
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {});
        };

        self.turnOn = function() {
            self.command("turnOn");
        };
        self.turnOff = function() {
            self.command("turnOff");
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

        self.statusOk = function() {
            return self.settings.getLocalData().plugins.ikea_tradfri.status == "ok";
        };

        /*self.sideBarInfoInterval = setInterval(function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/info",
                type: "GET",
                dataType: "json"
            }).done(self.onSidebarInfo);
        }, 1000);*/


        self.wizardSetCoapPath = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/wizard/coap_path",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    coap_path: $('#wizardIkeaTradfriCoapPath').val()
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {});
        };

        self.getWizardDevices = function(){
            return self.wizardDevices;
        }
        
        self.wizardTryConnect = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/wizard/tryConnect",
                type: "POST",
                //dataType: "json",
                data: JSON.stringify({
                    securityCode: $('#wizardIkeaTradfriSecurityCode').val(),
                    gateway: $('#wizardIkeaTradfriGateway').val()
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {
                //console.log('done', data);  
                self.wizardDevices(JSON.parse(data));              
                console.log(self.wizardDevices);
                self.wizardError(null);
            }).fail(function( jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        };

        self.onDataUpdaterPluginMessage = function(plugin, msg){
            if(plugin == 'ikea_tradfri'){
                if(msg.type == 'sidebar'){
                    console.log('data', plugin, msg);
                    self.onSidebarInfo(msg.payload);
                }
            }
        }

        self.onSidebarInfo = function(data){
            //console.log("onSidebarInfo ==>", data)
            self.sidebarInfo(data);
            //console.log("onSidebarInfo <== ", self.sidebarInfo())
        };

        self.sidebarShutdownAt = function(){
            return new Date(self.sidebarInfo().shutdownAt * 1000).toLocaleTimeString();
        }

        self.sidebarInfoShutdownPlanned = function(){
            return self.sidebarInfo().shutdownAt != null
        }

        self.postponeShutdown = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/postpone",
                type: "POST",
                dataType: "json",
                // data: JSON.stringify({
                //     securityCode: $('#wizardIkeaTradfriSecurityCode').val(),
                //     gateway: $('#wizardIkeaTradfriGateway').val()
                // }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function( jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.cancelShutdown = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/cancelShutdown",
                type: "POST",
                dataType: "json",
                // data: JSON.stringify({
                //     securityCode: $('#wizardIkeaTradfriSecurityCode').val(),
                //     gateway: $('#wizardIkeaTradfriGateway').val()
                // }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function( jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.shutdownNow = function(){
            $.ajax({
                url: BASEURL + "plugin/ikea_tradfri/sidebar/shutdownNow",
                type: "POST",
                dataType: "json",
                // data: JSON.stringify({
                //     securityCode: $('#wizardIkeaTradfriSecurityCode').val(),
                //     gateway: $('#wizardIkeaTradfriGateway').val()
                // }),
                contentType: "application/json; charset=UTF-8"
            }).done(self.onSidebarInfo).fail(function( jqXHR, textStatus, errorThrown) {
                //console.log('error',  jqXHR, textStatus, errorThrown);
                self.wizardError("Error when connection")
            });
        }

        self.onBeforeWizardFinish = function(){
            if($("#wizardIkeaTradfriDevices").val()){
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
        elements: ["#navbar_plugin_ikea_tradfri", "#settings_plugin_ikea_tradfri", "#wizard_plugin_ikea_tradfri", "#sidebar_plugin_ikea_tradfri"]
    });
});
