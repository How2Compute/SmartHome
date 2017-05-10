# Import time (for delay) library (for SmartHome api) and GPIO (for raspberry pi gpio)
from library import SmartHomeApi
import RPi.GPIO as GPIO
import time

# Board Pin 7  -> RED led pin
# Board Pin 11 -> GREEN led pin
# Board Pin 12 -> BLUE led pin.

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=10, api_key="api_eMxSb7n6G10Svojn3PlU5P6srMaDrFxmKAnWvnW6UyzmBG")

# Put the GPIO into board mode
GPIO.setmode(GPIO.BOARD)
# Set the Red, Green and Blue pins to output mode
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

# Create the last status and set it to UNKNOWN (so that it should trigger the update loop)
last_status = "UNKNOWN"

# Update function (checks if it's RED, GREEN, BLUE or something else)
def doUpdate(status):
    if status == "RED":
        GPIO.output(7, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
    elif status == "GREEN":
        GPIO.output(7, GPIO.LOW)
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
    elif status == "BLUE":
        GPIO.output(7, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)
    else:
        GPIO.output(7, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
    
    print("updating! (status: {})".format(status))
    
# Main loop
while True:
    # Query the API for the status
    status = api.GetDeviceStatus()
    # Check if the status has changed
    if last_status != status:
        # Call the update function, passing in the new status
        doUpdate(status)
        last_status = status
    # Wait for 1 second in order to not overload the API
    time.sleep(1)

