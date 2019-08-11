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
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.

        self.turnOn = function(){
            console.log('on');
            $.ajax({
				url: API_BASEURL + "plugin/ikea_tradfri",
				type: "POST",
				dataType: "json",
				data: JSON.stringify({
					command: "turnOn"
				}),
				contentType: "application/json; charset=UTF-8"
			}).done(function(data){
                
            });
        }
        self.turnOff = function(){
            console.log('off');
            $.ajax({
				url: API_BASEURL + "plugin/ikea_tradfri",
				type: "POST",
				dataType: "json",
				data: JSON.stringify({
					command: "turnOff"
				}),
				contentType: "application/json; charset=UTF-8"
			}).done(function(data){
                
            });
        }

    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: IkeaTradfriViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ /* "loginStateViewModel", "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_ikea-tradfri, #tab_plugin_ikea-tradfri, ...
        elements: [ '#navbar_plugin_ikea_tradfri' ]
    });
});
