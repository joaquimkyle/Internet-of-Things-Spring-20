import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

#setup board
GPIO.setmode(GPIO.BCM)

#setup pins
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.OUT)

#vars
beenPressed = False
ledOn = False

#setup mqtt client
broker_address="172.16.0.10"

def on_message(client, userdata, message):
    print(message.topic + " " + message.payload.decode('UTF-8'))
    if(str(message.topic) == "/pi_led"):
        if(str(message.payload.decode('UTF-8')) == "on"):
            GPIO.output(21, GPIO.HIGH) #turn pi LED on
        elif(str(message.payload.decode('UTF-8')) == "off"):
            GPIO.output(21, GPIO.LOW) #turn pi LED off
            
client = mqtt.Client() #create new mqtt client instance
client.connect(broker_address) #connect to broker 
client.subscribe("/pi_led") #subscribe to the right topic 
client.loop_start() #start client 
client.on_message=on_message #set the on message function

#loop
try:
    while True:
    
        #get button state
        buttonstate = GPIO.input(18)
        
        #if button just pressed down
        if (buttonstate and not beenPressed):      
            #set pressed flag
            beenPressed = True
        
            #toggle LED
            if (ledOn):
                client.publish("/arduino_led", "off") #tell arduino to turn LED off
                ledOn = False
            else:
                client.publish("/arduino_led", "on") #tell arduino to turn LED on
                ledOn = True
        
        #if button just released    
        if (not buttonstate and beenPressed):
            #set pressed flag
            beenPressed = False
            
        pass
        
except KeyboardInterrupt:
    pass
    
client.loop_stop() #stop client