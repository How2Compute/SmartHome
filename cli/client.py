from library import SmartHomeApi

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=1, api_key="api_LgyPqdKqxr8hiHcH5EHwBiNg62QsFJk4aYqb32YPIfhgQJ")
#api.RegisterDevice("hey", 0)
print("Can't test register device!")
print("Testing GetDevices...")
print(api.GetDevices())
print("Testing GetDeviceStatus for self...")
print(api.GetDeviceStatus())
print("Testing GetDeviceStatus for #2...")
print(api.GetDeviceStatus(device_id=2))
print("Testing SetNewStatus for self...")
api.SetNewStatus("TODO make this random") # doesn't work!
print("passed!" if api.GetDeviceStatus() == "TODO make this random" else "failed")
print("Testing SetNewStatus for self...")
api.SetNewStatus("TODO make this random", device_id=2) # doesn't work!
print("passed!" if api.GetDeviceStatus(device_id=2) == "TODO make this random" else "failed")
print("Can't test delete device!")
