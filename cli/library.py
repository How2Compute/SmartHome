import requests
import json

class SmartHomeApi():
    api_url = ""
    id = -1
    api_key = ""
    
    def __init__(self, url, id=-1, api_key="api_none"):
        self.api_url = url
        self.api_key = api_key
        self.id = id
    # API request helpers
    def PostApiRequest(self, target, payload):
        # Not sure if this works
        payload['api_key'] = self.api_key
        
        url = "{}/{}".format(self.api_url, target)
        response = requests.post(url, json=payload)
        if not response.ok:
            print("A request to {} failed with error code {}!".format(url, response.status_code))
            return False
        else:
            return True
            
    def PutApiRequest(self, target, payload):
        # Not sure if this works
        payload['api_key'] = self.api_key
        
        url = "{}/{}".format(self.api_url, target)
        response = requests.put(url, json=payload)
        if not response.ok:
            print("A request to {} failed with error code {}!".format(url, response.status_code))
            return False
        else:
            return True
            
    def DeleteApiRequest(self, target, payload):
        # Not sure if this works
        payload['api_key'] = self.api_key
        
        url = "{}/{}".format(self.api_url, target)
        response = requests.delete(url, json=payload)
        if not response.ok:
            print("A request to {} failed with error code {}!".format(url, response.status_code))
            return False
        else:
            return True
            
    def GetApiRequest(self, target, payload={}):
        # Not sure if this works
        payload['api_key'] = self.api_key
        
        url = "{}/{}".format(self.api_url, target)
        response = requests.get(url, json=payload)
        if not response.ok:
            print("A request to {} failed with error code {}!".format(url, response.status_code))
            return {
                'success': False,
                'results': None
                }
        else:
            return {
                'success': True,
                'results': response.json()
                }
    
    #class Devices():
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
            return True
    
    def GetDevices(self):
        request = self.GetApiRequest('devices')
        if not request['success']:
            return None
        else:
            return request['results']
    
    def GetDeviceStatus(self, device_id = -1):
        if device_id == -1:
            device_id = self.id
        request = self.GetApiRequest('devices/{}'.format(device_id))
        if not request['success']:
            return None
        else:
            return request['results']['status']
    
    def SetNewStatus(self, status, device_id = -1):
        if device_id == -1:
            device_id = self.id
        request = self.PutApiRequest('devices/{}'.format(device_id), {'status': status})
        # request is true/false so return that
        return request
        
    def DeleteDevice(self, device_id=-1):
        if device_id == -1:
            device_id = self.id
        request = self.DeleteApiRequest('devices/{}'.format(device_id), {})
        # request is true/false so return that
        return request
    
    # class Users():
    def GetUsers(self):
        request = self.GetApiRequest('users', {})
        
        if not request['success']:
            return None
        else:
            return request['results']
            
    def GetUser(self, user_id):
        request = self.GetApiRequest('users/{}'.format(user_id))
        
        if not request['success']:
            return None
        else:
            return request['results']
    
    
    def AddPreference(self, user_id, key, value):
        request = self.PostApiRequest('users/{}/preferences'.format(user_id), {})
        
        return request
        
    def UpdatePreference(self, user_id, key, value):
        request = self.PutApiRequest('users/{}/preferences/{}'.format(user_id, key), { "value": value })
        return request
    
    def DeletePreference(self):
        request = self.DeleteApiRequest('users/{}/preferences/{}'.format(user_id, key), {})
        return request
    
    # class Portal():
    def GetDeviceActive(self, device_id = -1):
        if device_id == -1:
            request = self.GetApiRequest('portal/approved', {})
        else:
            request = self.GetApiRequest('portal/approved/{}'.format(device_id), {})
            
        if request['success'] == False:
            return None
        else:
            return request['results']
    
    def GetPermissionLevel(self, device_id = -1):
        if device_id == -1:
            request = self.GetApiRequest('portal/permissions', {})
        else:
            request = self.GetApiRequest('portal/permissions', {})
        
        # Return -1 if an error occured
        if request['success'] == False:
            return -1
        # Otherwise return the level we got back from the request
        else:
            # May not work!
            results = request['results']
            return results['level']
    
    def ApproveDevice(self, device_id, status):
        request = self.PostApiRequest('portal/approved/{}'.format(device_id), {})
        return request
    
        """   
    class Users():
        def NotifyUser() - TODO
        def GetPrerences() - TODO
        """