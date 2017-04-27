import requests
import json

class SmartHomeApi():
    api_url = ""
    id = -1
    api_key = ""
    
    def __init__(self, url, id=-1, api_key="api_none"):
        self.api_url = url
        self.api_key = api_key
    
    
    def RegisterDevice(self, name, permission_level):
        payload = {
            'name': name, 
            'permission_level': permission_level
        }
        jsonData = json.dumps(payload)
        url = "{}/devices".format(self.api_url)
        response = requests.post(url, json=payload)
        if not response.ok:
            print("{} delivered a NOK response!".format(json.dumps(payload)))
            return False
        else:
            
            id = response.json()['id']
            api_key = response.json()['api_key']
            
            
        print(response)
            
        """   
    class Devices():
        def GetDevices()
        def GetDeviceStatus()
        def SetNewStatus()
        def DeleteDevice()
    class Users():
        def ListUsers()
        def GetUser()
        def NotifyUser()
        def SetPreference()
        def DeletePreference()
    class Portal():
        def GetDeviceActive()
        def GetPermissionLevel()
        def ApproveDevice()
        """