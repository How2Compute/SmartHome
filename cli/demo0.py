# Import time (for delay) library (for SmartHome api) and GPIO (for raspberry pi gpio)
from library import SmartHomeApi
import RPi.GPIO as GPIO
import time
from datetime import datetime

# 7  -> LED

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=10, api_key="api_LgyPqdKqxr8hiHcH5EHwBiNg62QsFJk4aYqb32YPIfhgQJ")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

last_status = "UNKNOWN"

def doUpdate(status):
    if status == "ON":
        GPIO.output(7, GPIO.HIGH)
    else:
        GPIO.output(7, GPIO.LOW)
    
    print("updating! (status: {})".format(status))

while True:
    status = api.GetDeviceStatus()
    if last_status != status:
        # Changed!
        doUpdate(status)
        last_status = status
    time.sleep(1)