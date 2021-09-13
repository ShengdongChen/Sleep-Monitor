import paho.mqtt.client as mqtt # import MQTT library
from gpiozero import MotionSensor
import RPi.GPIO as GPIO
import time
from datetime import datetime
# for handling CTRL+C
import signal, sys

sound = 25
motion_pin = 24
motion = MotionSensor(motion_pin)
numOfMostions = 0
numOfSounds = 0
fallAsleep = False

soundLogFile = None
motionLogFile = None

soundLog = []
motionLog = []

def callback(sound):
    global numOfSounds, soundLog
    if GPIO.input(sound):
        timeNow = datetime.now()
        numOfSounds = numOfSounds + 1
        print (str(timeNow) + "     Sound Detected")
        soundLog.append(timeNow)
    else:
        timeNow = datetime.now()
        numOfSounds = numOfSounds + 1
        print (str(timeNow) + "     Sound Detected")
        soundLog.append(timeNow)

def main():
    global broker_ip, client, start_time, fallAsleep, soundLogFile, motionLogFile
    signal.signal(signal.SIGINT, signal_handler)
    broker_ip = "71.71.34.73"
    start_time = datetime.now()
    
    soundLogFile = open("soundLog.txt", "a+")
    motionLogFile = open("motionLog.txt", "a+")

    client = mqtt.Client(client_id="SleepTracker", clean_session=True)
    client.on_connect = on_connect
    client.will_set("Status", payload="offline", qos=2, retain=True)

    client.connect(broker_ip)
    client.loop_start()
    while True:
        checkSleep()
        if (fallAsleep == True):
            sleepTrack()

# handle MQTT connection confirmation
def on_connect(param_client, userdata, message, rc):
    print("Connected to broker at: " + broker_ip)
    client.publish("Status", payload="online", qos=2, retain=True) # publish that sleep tracker is online

def checkPreSleepMotion(numberCheck):
    if GPIO.input(motion_pin):
        numberCheck += 1
        print("Pre-Sleep Motion Detected")
    return numberCheck

def checkSleep():
    global fallAsleep
    if (fallAsleep == True):
        pass
    else:
        numberCheck = 0
        # Countdown 5 minutes to check if user is sleeping
        countdown = 0
        while countdown > 0:
            numberCheck = checkPreSleepMotion(numberCheck)
            time.sleep(1)
            countdown -= 1
            print(countdown)
        if (numberCheck == 0 and countdown == 0):
            fallAsleep = True

def sleepTrack():
    global numOfMostions, motionLog
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sound, GPIO.IN)
    GPIO.add_event_detect(sound, GPIO.BOTH, bouncetime = 300)
    GPIO.add_event_callback(sound, callback)

    while True:
        motion.wait_for_motion()
        timeNow = datetime.now()
        numOfMostions += 1
        print(str(timeNow) + "     Motion Detected")
        motionLog.append(timeNow)
        motion.wait_for_no_motion()
        pass

# handle CTRL+C
def signal_handler(sig, frame):
    global client, end_time, motionLogFile, soundLogFile

    for i in motionLog:
        motionLogFile.write(str(i))
        motionLogFile.write("\n")
    for i in soundLog:
        soundLogFile.write(str(i))
        soundLogFile.write("\n")

    motionLogFile.close()
    soundLogFile.close()

    soundFile = open("soundLog.txt", "rb")
    motionFile = open("motionLog.txt", "rb")
    soundByte = bytearray(soundFile.read())
    motionByte = bytearray(motionFile.read())

    print('\nDisconnecting gracefully')
    end_time = datetime.now()
    if (client != None):
        client.publish("Status", payload="offline", qos=2, retain=True) # publish that that sleep tracker is offline
        client.publish("Motion", payload=str(numOfMostions), qos=2, retain=True)
        client.publish("Sound", payload=str(numOfSounds), qos=2, retain=True)
        client.publish("Time", payload=str(end_time - start_time), qos=2, retain=True)
        client.publish("MotionLog", payload= motionByte, qos=2, retain=True)
        client.publish("SoundLog", payload= soundByte, qos=2, retain=True)

        print("Please wait for sending data.")
        time.sleep(5)
        client.disconnect()
    # wait before ending the program
    time.sleep(0.5)
    sys.exit(0)

if __name__ == "__main__":
    main()