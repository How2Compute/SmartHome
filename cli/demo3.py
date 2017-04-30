from library import SmartHomeApi

# Create and register the client
api = SmartHomeApi("http://localhost:5000/api/0.1")
api.RegisterDevice("CoolName", 5)