from library import SmartHomeApi

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1")

api.RegisterDevice("CoolName", 5)