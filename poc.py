import requests
import json

APPLIANCE_URL = 'https://api.connectlife.io/api/v1/appliance/'
access_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' #use your own token

### get properties
def getApplianceProperties(applianceId):
    global APPLIANCE_URL
    api_url = APPLIANCE_URL + applianceId
    propertiesResponse = requests.get(api_url, headers={'Authorization': 'Bearer ' + access_token})
    applianceProperties = propertiesResponse.json()[0]['properties']
    return applianceProperties

def getApplianceMetadata(applianceId):
    global APPLIANCE_URL
    api_url = APPLIANCE_URL + 'metadata/' + applianceId + '/en'
    metadataResponse = requests.get(api_url, headers={'Authorization': 'Bearer ' + access_token})
    applianceMetaData = metadataResponse.json()[0]['propertyMetadata']
    return applianceMetaData

def addPowerOnToJson(inputJson):
    # adds "Power On" to existing command
    z = json.loads(inputJson)
    z[0]['properties'].update({"Power": "1"})
    return json.dumps(z)

def sendAppliancePostRequest(jsonData):
     global APPLIANCE_URL
     global access_token
     response = requests.post(
        APPLIANCE_URL,
        headers     = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'},
        data        = jsonData
     )
     print(response)

class appliance:
    def __init__(self, jsonData):
        self.id         = jsonData['id']
        self.name       = jsonData['name']
        self.type       = jsonData['type']
        self.status     = jsonData['status']
    
    def updateProperties(self):
        newProperties = getApplianceProperties(self.id)
        self.power               = newProperties['Power']
        self.temperatureUnit     = newProperties['TemperatureUnit']
        self.setTemperature      = newProperties['SetTemperature']
        self.currentTemperature  = newProperties['CurrentTemperature']
        self.mode                = newProperties['Mode']
        self.fanSpeed            = newProperties['FanSpeed']

    def getCurrentStatus(self):
        outputStr = 'Current Device Status:\n'
        outputStr += '\nPower:               ' + self.power
        outputStr += '\ntemperatureUnit:     ' + self.temperatureUnit
        outputStr += '\nsetTemperature:      ' + self.setTemperature
        outputStr += '\ncurrentTemperature:  ' + self.currentTemperature
        outputStr += '\nmode:                ' + self.mode
        outputStr += '\nfanSpeed:            ' + self.fanSpeed
        outputStr += '\nid:                  ' + self.id
        outputStr += '\nname:                ' + self.name
        outputStr += '\ntype:                ' + self.type
        outputStr += '\nstatus:              ' + self.status
        outputStr += '\n'
        print(outputStr)

    def updateMetadata(self):
        newMetadata = getApplianceMetadata(self.id)
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
        sendAppliancePostRequest(jsonDataForPost)

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
        sendAppliancePostRequest(jsonDataForPost)

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
        sendAppliancePostRequest(jsonDataForPost)


ApplianceResponse = requests.get(APPLIANCE_URL, headers={'Authorization': 'Bearer ' + access_token})
#ApplianceResponse.json()

device = appliance(ApplianceResponse.json()[0]) # change the index [0] if you have more than one device

print('Device Name: ' + device.name)

device.updateProperties()
device.updateMetadata()

device.getCurrentStatus()

print('Possible SystemMode values: ' + str(', '.join(device.systemModes.keys())))
print('Possible fan values: ' +  str(', '.join(device.fanValues.keys())))

device.setSystemMode('Cool', True)
device.changeTemperature('68', 'Fahrenheit degree', True)
device.setFanSpeed('Medium', True)
