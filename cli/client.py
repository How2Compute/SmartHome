from library import SmartHomeApi

api = SmartHomeApi("http://localhost:8080/api/0.1")
api.RegisterDevice("hey", 0)

print(api.GetDevices())