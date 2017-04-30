# Import time (for delay) library (for SmartHome api) and GPIO (for raspberry pi gpio)
from library import SmartHomeApi
import RPi.GPIO as GPIO
import time

# 7  -> RED
# 11 -> GREEN
# 12 -> BLUE

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=10, api_key="api_eMxSb7n6G10Svojn3PlU5P6srMaDrFxmKAnWvnW6UyzmBG")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

last_status = "UNKNOWN"

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
    
while True:
    status = api.GetDeviceStatus()
    if last_status != status:
        # Changed!
        doUpdate(status)
        last_status = status
    time.sleep(1)

