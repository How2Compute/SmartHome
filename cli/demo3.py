# Import the SmartHome! library
from library import SmartHomeApi

# Connect to the API, running on localhost, port 5000
api = SmartHomeApi("http://localhost:5000/api/0.1")
# Register a device with the name: "CoolName" and permission level 5 
api.RegisterDevice("CoolName", 5)
