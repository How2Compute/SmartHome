from library import SmartHomeApi
import time
# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=1, api_key="api_LgyPqdKqxr8hiHcH5EHwBiNg62QsFJk4aYqb32YPIfhgQJ")

last_status = "UNKNOWN"
def doUpdate(status):
    # TODO
    print("updating! (status: {})".format(status))
    
while True:
    status = api.GetDeviceStatus()
    if last_status != status:
        # Changed!
        doUpdate(status)
        last_status = status
    time.sleep(1)
