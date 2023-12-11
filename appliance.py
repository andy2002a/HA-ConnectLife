import requests
import json

def getApplianceProperties(applianceUrl, accessToken, applianceId):
    api_url = applianceUrl + applianceId
    propertiesResponse = requests.get(api_url, headers={'Authorization': 'Bearer ' + accessToken})
    applianceProperties = propertiesResponse.json()[0]['properties']
    return applianceProperties

def getApplianceMetadata(applianceUrl, accessToken, applianceId):
    api_url = applianceUrl + 'metadata/' + applianceId + '/en'
    metadataResponse = requests.get(api_url, headers={'Authorization': 'Bearer ' + accessToken})
    applianceMetaData = metadataResponse.json()[0]['propertyMetadata']
    return applianceMetaData

def addPowerOnToJson(inputJson):
    # adds "Power On" to existing command
    z = json.loads(inputJson)
    z[0]['properties'].update({"Power": "1"})
    return json.dumps(z)

def sendAppliancePostRequest(applianceUrl, accessToken, jsonData):
     response = requests.post(
        applianceUrl,
        headers     = {'Authorization': 'Bearer ' + accessToken, 'Content-Type': 'application/json'},
        data        = jsonData
     )
     print(response)

class appliance:
    def __init__(self, applianceUrl, accessToken, jsonData):
        self.applianceUrl   = applianceUrl
        self.accessToken    = accessToken
        self.id             = jsonData['id']
        self.name           = jsonData['name']
        self.type           = jsonData['type']
        self.status         = jsonData['status']
        self.updateProperties()
        self.getCurrentStatus()

    def updateProperties(self):
        newProperties = getApplianceProperties(self.applianceUrl, self.accessToken, self.id)
        self.power               = newProperties['Power']
        self.temperatureUnit     = newProperties['TemperatureUnit']
        self.setTemperature      = newProperties['SetTemperature']
        self.currentTemperature  = newProperties['CurrentTemperature']
        self.mode                = newProperties['Mode']
        self.fanSpeed            = newProperties['FanSpeed']

    def getCurrentStatus(self):
        outputStr = 'Current Device Status:\n'
        outputStr += '\nname:                ' + self.name
        outputStr += '\nid:                  ' + self.id
        outputStr += '\nstatus:              ' + self.status
        outputStr += '\ntype:                ' + self.type
        outputStr += '\nPower:               ' + self.power
        outputStr += '\ntemperatureUnit:     ' + self.temperatureUnit
        outputStr += '\nsetTemperature:      ' + self.setTemperature
        outputStr += '\ncurrentTemperature:  ' + self.currentTemperature
        outputStr += '\nmode:                ' + self.mode
        outputStr += '\nfanSpeed:            ' + self.fanSpeed
        outputStr += '\n'
        return outputStr

    def updateMetadata(self):
        newMetadata = getApplianceMetadata(self.applianceUrl, self.accessToken, self.id)
        for metaDataObject in newMetadata:
            if (metaDataObject['key'] == 'FanSpeed'):
                fanValues = metaDataObject['enumValues']
                self.fanValues = {}
                for value in fanValues:
                        self.fanValues.update({fanValues[value]['key']: value})
            elif (metaDataObject['key'] == 'SetTemperature'):
                self.minValueCelsius = metaDataObject['minValueCelsius']
                self.maxValueCelsius = metaDataObject['maxValueCelsius']
                self.minValueFahrenheit = metaDataObject['minValueFahrenheit']
                self.maxValueFahrenheit = metaDataObject['maxValueFahrenheit']
            elif (metaDataObject['key'] == 'TemperatureUnit'):
                tempUnitValues = metaDataObject['enumValues']
                self.possibleTemperatureUnits = {}
                for value in tempUnitValues:
                        self.possibleTemperatureUnits.update({tempUnitValues[value]['label']: value})
            elif (metaDataObject['key'] == 'Mode'):
                self.systemModes = {'Fan only': '0', 'Heat': '1', 'Cool': '2', 'Dry': '3'}  ## Remove this when bug resolved
                # There is a bug where the API does not match the modes correctly
                #
                #systemModes = metaDataObject['enumValues']
                #self.systemModes = {}
                #for mode in systemModes:
                #        self.systemModes.update({systemModes[mode]['key']: mode})

    def changeTemperature(self, newTempValue, tempUnit, powerOnWithChange):
        jsonDataForPost = json.dumps(
            [{
                'id': self.id,
                'properties': {
                        'SetTemperature': str(newTempValue),
                        'TemperatureUnit': self.possibleTemperatureUnits[tempUnit]
                }
            }]
        )
        # Also power on the device if the temperature is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        sendAppliancePostRequest(self.applianceUrl, self.accessToken, jsonDataForPost)

    def setFanSpeed(self, fanSpeed, powerOnWithChange):
        jsonDataForPost = json.dumps(
            [{
                'id': self.id,
                'properties': {
                        'FanSpeed': str(self.fanValues[fanSpeed])
                }
            }]
        )
        # Also power on the device if the speed is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        sendAppliancePostRequest(self.applianceUrl, self.accessToken, jsonDataForPost)

    def setSystemMode(self, systemMode, powerOnWithChange):
        jsonDataForPost = json.dumps(
            [{
                'id': self.id,
                'properties': {
                        'Mode': str(self.systemModes[systemMode])
                }
            }]
        )
        # Also power on the device if the speed is changed
        if powerOnWithChange:
            jsonDataForPost = addPowerOnToJson(jsonDataForPost)
        sendAppliancePostRequest(self.applianceUrl, self.accessToken, jsonDataForPost)
