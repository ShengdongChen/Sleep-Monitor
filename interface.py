# hello_psg.py

import PySimpleGUI as sg
import paho.mqtt.client as mqtt
import signal, sys

broker = None

client = None

TOPICS = [("Status/SleepTracker", 2), ("motion/SleepTracker", 2), ("sound/SleepTracker", 2), ("time/SleepTracker", 2)]

layout = [
    [sg.Text("Hello from SleepTracker")], 
    [sg.Button("Close")],
    [sg.Text("Start Status: "), sg.Text("offline", key='statusKey')],
    [sg.Text("motions: "), sg.Text("N/A", key='mKey')],
    [sg.Text("number of sounds: "), sg.Text("N/A", key='soundKey')],
    [sg.Text("Total time sleeped: "), sg.Text("00:00:00", key='tKey')],
    ]

# Create the window
window = sg.Window("Sleep Tracker", layout, margins=(400, 200))

# The callback for when client connects to the server
def on_connect(client, userdata, flags, rc):
    global broker
    if rc == 0:
        client.subscribe(TOPICS)
        print("You have now connected to the broker\n")
    else:
        print("Connection failed Returned code =",rc)
        print("\n")

# When client gets a messsage
def on_message(client, userdata, message):
    topic = str(message.topic)
    content = str(message.payload.decode())
    if topic == "Status/SleepTracker":
        window['statusKey'].update(content)
    elif topic == "motion/SleepTracker":
        window['mKey'].update(content)
    elif topic == "sound/SleepTracker":
        window['soundKey'].update(content)
    elif topic == "time/SleepTracker":
        window['tKey'].update(content)

# The signal handler for when client press ctrl + c
def signal_handler(sig, frame):
    print("You have now disconnected by pressing Ctrl+C")
    outputFile.close()
    sys.exit(0)

# Create an event loop
def main():    
    global broker, client
    # set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    # initialize client
    client = mqtt.Client("interface")
    client.on_connect = on_connect
    client.on_message = on_message
    broker = "71.71.34.73"
    client.connect(broker)
    client.loop_start()
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "Close" or event == sg.WIN_CLOSED:
            break

        
    window.close()

main()