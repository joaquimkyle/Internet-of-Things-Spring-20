import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO
import datetime

#setup board
GPIO.setmode(GPIO.BCM)

#setup pins
GPIO.setup(21, GPIO.OUT)

#setup influxdb client
dbclient = InfluxDBClient('127.0.0.1', 8086, 'root', 'floho5310', 'mydb')

#setup mqtt client
broker_address="172.16.0.10"

def on_message(client, userdata, message):
    print(message.topic + " " + message.payload.decode('UTF-8'))
    
    if(str(message.topic) == "/light"):
        receiveTime = datetime.datetime.utcnow()
        value = message.payload.decode('UTF-8')
        json_body = [
            {
                "measurement": 'light',
                "time": receiveTime,
                "fields": {
                    "value": int(value)
                }
            }
        ]
        
        dbclient.write_points(json_body)
        print("Finished writing to InfluxDB")
        
    if(str(message.topic) == "/pi_led"):
        if(str(message.payload.decode('UTF-8')) == "on"):
            GPIO.output(21, GPIO.HIGH) #turn LED on
        elif(str(message.payload.decode('UTF-8')) == "off"):
            GPIO.output(21, GPIO.LOW) #turn LED off
            
client = mqtt.Client() #create new mqtt client instance
client.connect(broker_address) #connect to broker 
client.subscribe("/pi_led") #subscribe to the topic for led state
client.subscribe("/light") #subscribe to the topic for photoresistor reading 
client.loop_start() #start client 
client.on_message=on_message #set the on message function

#loop
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
    
client.loop_stop() #stop mqtt client
GPIO.cleanup()