# Import time (for delay) library (for SmartHome api) and GPIO (for raspberry pi gpio)
from library import SmartHomeApi
import RPi.GPIO as GPIO
import time
from datetime import datetime

# Board Pin 7  -> LED

# Connect to the API on localhost, port 5000 with the credentials of id->10 and api_key->api_Lg...QJ
api = SmartHomeApi("http://localhost:5000/api/0.1", id=10, api_key="api_LgyPqdKqxr8hiHcH5EHwBiNg62QsFJk4aYqb32YPIfhgQJ")

# Set the raspberry to use BOARD mode (how to handle pin numbers)
GPIO.setmode(GPIO.BOARD)
# Set GPIO pin 7 as an output
GPIO.setup(7, GPIO.OUT)

# Set the last status to UNKNOWN (so that it should update in the later loop)
last_status = "UNKNOWN"

# Function that handles updating the light
def doUpdate(status):
    if status == "ON":
        # Switch the LED on.
        GPIO.output(7, GPIO.HIGH)
    else:
        # Switch the LED off.
        GPIO.output(7, GPIO.LOW)
    
    print("updating! (status: {})".format(status))

# Main Loop
while True:
    # Query the API (and in turn the HUB) for the apps' status
    status = api.GetDeviceStatus()
    # Check if the status has changed
    if last_status != status:
        # If it has, call the update function passing in the new status
        doUpdate(status)
        last_status = status
    # Wait for 1 second in order to not stress the API
    time.sleep(1)
