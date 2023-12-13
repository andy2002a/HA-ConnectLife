import requests
import json


def addPowerOnToJson(inputJson):
    # adds "Power On" to existing command
    z = json.loads(inputJson)
    z[0]["properties"].update({"Power": "1"})
    return json.dumps(z)


class appliance:
    def __init__(self, applianceUrl, accessToken, jsonData):
        self._applianceUrl = applianceUrl
        self._accessToken = accessToken
        self._id = jsonData["id"]
        self._name = jsonData["name"]
        self._type = jsonData["type"]
        self._status = jsonData["status"]
        self.updateProperties()
        self.getCurrentStatus()

    def getApplianceProperties(self):
        api_url = self.applianceUrl + self.id
        propertiesResponse = requests.get(
            api_url, headers={"Authorization": "Bearer " + self.accessToken}
        )
        applianceProperties = propertiesResponse.json()[0]["properties"]
        return applianceProperties

    def updateProperties(self):
        newProperties = self.getApplianceProperties()
        self._power = newProperties["Power"]
        self._temperatureUnit = newProperties["TemperatureUnit"]
        self._setTemperature = newProperties["SetTemperature"]
        self._currentTemperature = newProperties["CurrentTemperature"]
        self._mode = newProperties["Mode"]
        self._fanSpeed = newProperties["FanSpeed"]

    def getCurrentStatus(self):
        outputStr = "Current Device Status:\n"
        outputStr += "\nname:                " + self._name
        outputStr += "\nid:                  " + self._id
        outputStr += "\nstatus:              " + self._status
        outputStr += "\ntype:                " + self._type
        outputStr += "\nPower:               " + self._power
        outputStr += "\ntemperatureUnit:     " + self._temperatureUnit
        outputStr += "\nsetTemperature:      " + self._setTemperature
        outputStr += "\ncurrentTemperature:  " + self._currentTemperature
        outputStr += "\nmode:                " + self._mode
        outputStr += "\nfanSpeed:            " + self._fanSpeed
        outputStr += "\n"
        return outputStr

    def getApplianceMetadata(self):
        api_url = self._applianceUrl + "metadata/" + self._id + "/en"
        metadataResponse = requests.get(
            api_url, headers={"Authorization": "Bearer " + self._accessToken}
        )
        applianceMetaData = metadataResponse.json()[0]["propertyMetadata"]
        return applianceMetaData

    def updateMetadata(self):
        newMetadata = self.getApplianceMetadata()
        for metaDataObject in newMetadata:
            if metaDataObject["key"] == "FanSpeed":
                fanValues = metaDataObject["enumValues"]
                self._fanValues = {}
                for value in fanValues:
                    self._fanValues.update({fanValues[value]["key"]: value})
            elif metaDataObject["key"] == "SetTemperature":
                self._minValueCelsius = metaDataObject["minValueCelsius"]
                self._maxValueCelsius = metaDataObject["maxValueCelsius"]
                self._minValueFahrenheit = metaDataObject["minValueFahrenheit"]
                self._maxValueFahrenheit = metaDataObject["maxValueFahrenheit"]
            elif metaDataObject["key"] == "TemperatureUnit":
                tempUnitValues = metaDataObject["enumValues"]
                self._possibleTemperatureUnits = {}
                for value in tempUnitValues:
                    self._possibleTemperatureUnits.update(
                        {tempUnitValues[value]["label"]: value}
                    )
            elif metaDataObject["key"] == "Mode":
                self._systemModes = {
                    "Fan only": "0",
                    "Heat": "1",
                    "Cool": "2",
                    "Dry": "3",
                }  ## Remove this when bug resolved
                # There is a bug where the API does not match the modes correctly
                #
                # systemModes = metaDataObject['enumValues']
                # self.systemModes = {}
                # for mode in systemModes:
                #        self.systemModes.update({systemModes[mode]['key']: mode})

    def sendAppliancePostRequest(self, jsonData):
        response = requests.post(
            self._applianceUrl,
            headers={
                "Authorization": "Bearer " + self._accessToken,
                "Content-Type": "application/json",
            },
            data=jsonData,
        )
        print(response)

    def jsonPropertiesBuilder(self, propertiesDict):
        jsonData = json.dumps(
            [
                {
                    "id": self._id,
                    "properties": propertiesDict,
                }
            ]
        )
        return jsonData

    def setTemperature(self, newTempValue, powerOnWithChange):
        jsonDataForPost = self.jsonPropertiesBuilder(
            {"SetTemperature": str(newTempValue)}
        )
        # Also power on the device if the temperature is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        #
        self.sendAppliancePostRequest(jsonDataForPost)

    def setTemperatureUnit(self, tempUnit):
        jsonDataForPost = self.jsonPropertiesBuilder(
            {"TemperatureUnit": self._possibleTemperatureUnits[tempUnit]}
        )
        self.sendAppliancePostRequest(jsonDataForPost)

    def setFanSpeed(self, fanSpeed, powerOnWithChange=False):
        jsonDataForPost = self.jsonPropertiesBuilder(
            {"FanSpeed": str(self._fanValues[fanSpeed])}
        )
        # Also power on the device if the speed is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        self.sendAppliancePostRequest(jsonDataForPost)

    def setSystemMode(self, systemMode, powerOnWithChange=False):
        jsonDataForPost = self.jsonPropertiesBuilder(
            {"Mode": str(self._systemModes[systemMode])}
        )
        # Also power on the device if the speed is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        self.sendAppliancePostRequest(jsonDataForPost)
