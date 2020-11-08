def on_event(self, event, payload):
        scheduleStop = False
        if event == 'PrintDone' and self._settings.get_boolean(['on_done']):
            scheduleStop = True
        if event == 'PrintFailed' and self._settings.get_boolean(['on_failed']):
            scheduleStop = True
        if scheduleStop:
            stop_timer=int( self._settings.get(['stop_timer']) )
            self.planStop(stop_timer)


@octoprint.plugin.BlueprintPlugin.route("/state", methods=["GET"])
def getState(self):
    res = self.getStateData()

    return flask.make_response(json.dumps(res, indent=4), 200)

@octoprint.plugin.BlueprintPlugin.route("/state", methods=["POST"])
def setState(self):
    state = flask.request.json['state']

    if state == 1 or state == True:
        self.turnOn()
    else:
        self.turnOff()

    data = self.run_gateway_get_request('/15001/{}'.format(self._settings.get(['selected_outlet'])))
    state = data["3312"][0]["5850"]==1

    res = dict(
        state=state
    )

    return flask.make_response(json.dumps(res, indent=4), 200)