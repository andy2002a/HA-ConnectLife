from appliance import *
import requests
import json

APPLIANCE_URL = 'https://api.connectlife.io/api/v1/appliance/'
ACCESS_TOKEN = 'xxxxxx' #use your own token

class connectLife():
    def __init__(self, applianceUrl, accessToken):
        self.applianceUrl = applianceUrl
        self.accessToken = accessToken
        self.devicesDict = {}
        self.generateDevicesDict()
        self.updateAllDevicesStatus()

    def getAllDevicesJson(self):
        ApplianceResponse = requests.get(self.applianceUrl, headers={'Authorization': 'Bearer ' + self.accessToken})
        return ApplianceResponse.json()

    def generateDevicesDict(self):
        allDevicesJsonResponse = self.getAllDevicesJson()
        for deviceJson in allDevicesJsonResponse:
            newDevice =  appliance(self.applianceUrl, self.accessToken, deviceJson)
            self.devicesDict[newDevice.name] = newDevice

    def getAllDevicesName(self):
        return self.devicesDict.keys()

    def getDeviceCurrentStatus(self, deviceName):
        print(self.devicesDict[deviceName].getCurrentStatus())

    def getAllDevicesStatus(self):
        for device in self.devicesDict.keys():
            self.getDeviceCurrentStatus(device)

    def updateDeviceStatus(self, deviceName):
        self.devicesDict[deviceName].updateProperties()
        self.devicesDict[deviceName].updateMetadata()

    def updateAllDevicesStatus(self):
        for device in self.devicesDict.keys():
            self.updateDeviceStatus(device)

    def changeDeviceTemperature(self, deviceName):
        UnitInput = input('''What temperature Unit do you want to set? (C/F) ''')

        if UnitInput.lower() == 'f':
            temperatureUnit = 'Fahrenheit degree'
            validMinTemp = self.devicesDict[deviceName].minValueFahrenheit
            validMaxTemp = self.devicesDict[deviceName].maxValueFahrenheit
        elif UnitInput.lower() == 'c':
            temperatureUnit = 'Celsius degree'
            validMinTemp = self.devicesDict[deviceName].minValueCelsius
            validMaxTemp = self.devicesDict[deviceName].maxValueCelsius

        desiredTemp = input('Temperature do you want to set? Valid values: (' + validMinTemp + '-' + validMaxTemp + ')')

        self.devicesDict[deviceName].changeTemperature(desiredTemp, temperatureUnit, True)

    def changeDeviceSettings(self, deviceName):
        options = input('''What do you want to change?
              1 Temperature
              2 Fan Speed
              3 System Mode

              Use comma to separate multiple options.
            ''')

        deviceToChange = self.devicesDict[deviceName]

        for option in options.split(','):
            if option == '1':
                #change temp

                self.changeDeviceTemperature(deviceName)
                a=1
            elif option == '2':
                #change fan speed
                a=1
            elif option == '3':
                #change System Mode
                a=1



connectLifeAppliances = connectLife(APPLIANCE_URL, ACCESS_TOKEN)


print('Found the following devices: ' + ', '.join(connectLifeAppliances.getAllDevicesName()))

print('''Options:\n\n
      1 Get status of all devices
      2 Get status of single device
      3 Change device settings
      4 Update all device status
      ''')

action = input('What do you want to do? ')

if action == '1':
    connectLifeAppliances.getAllDevicesStatus()

elif action == '2':
    deviceName = input('What is the name of the device? ')
    connectLifeAppliances.getDeviceCurrentStatus(deviceName)

elif action == '3':
    deviceName = input('What is the name of the device? ')
    connectLifeAppliances.changeDeviceSettings(deviceName)

elif action == '4':
    connectLifeAppliances.updateAllDevicesStatus()
