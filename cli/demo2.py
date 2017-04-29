# Import time (for delay) library (for SmartHome api) and GPIO (for raspberry pi gpio)
from library import SmartHomeApi
import RPi.GPIO as GPIO
import time
from datetime import datetime

# 7  -> RED
# 11 -> GREEN
# 12 -> BLUE

# Create the client with pre-existing credentials
api = SmartHomeApi("http://localhost:5000/api/0.1", id=10, api_key="api_eMxSb7n6G10Svojn3PlU5P6srMaDrFxmKAnWvnW6UyzmBG")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

last_status = "UNKNOWN"


while True:
    preferences = api.GetUserPrefences(2)['results']
    
    print(preferences)
    
    #preference = filter(lambda preference: preferences['key'] == 'bedtime', preferences)
    preference = (item for item in preferences if item["key"] == "bedtime").next()
    
    """
    if not 'bedtime' in preferences:
        print("Could not find 'bedtime' preference!")
        api.AddPreference(2, "bedtime", "00:00")
        print("Created bedtime preference! Please set it to the correct value in your dashboard")
        break
    
    preference = preferences["bedtime"]
    """
    
    if not preference:
        print("Could not fin 'bedtime' preference!")
        api.AddPreference(2, "bedtime", "00:00")
        print("Created bedtime preference! Please set it to the correct value in your dashboard")
    else:
        bedtime = preference['value']
        if not bedtime:
            print("Unexpected error occured!")
        else:
            print(bedtime)
            time_str = datetime.now().strftime('%H:%M')
            print("time: {}".format(time_str))
            
            bedtime_dt = datetime.strptime(bedtime, "%H:%M")
            time_hm = datetime.strptime(time_str, "%H:%M")
            
            if time_hm >= bedtime_dt:
                print("Going to bed! Currently: {}, going to bed at {}".format(time_str, bedtime))
                GPIO.output(7, GPIO.LOW)
            else:
                print("Not yet time for bed. Currently: {}, going to bed at {}".format(time_str, bedtime))
                GPIO.output(7, GPIO.HIGH)
        
    
    time.sleep(1)

