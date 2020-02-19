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

#vars
light_avg = 0

#setup mqtt client
broker_address="172.16.0.10"

def on_message(client, userdata, message):
    print(message.topic + " " + message.payload.decode('UTF-8'))
    if(str(message.topic) == "/pi_led"):
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
            
client = mqtt.Client() #create new mqtt client instance
client.connect(broker_address) #connect to broker 
client.subscribe("/pi_led") #subscribe to the right topic 
client.loop_start() #start client 
client.on_message=on_message #set the on message function

#loop
while True:
    try:
        #query db for average light value from past 10 seconds
        query = 'select mean("value") from "light" where "time" > now() - 10s'
        
        result = dbclient.query(query)
        
        try:
            light_avg = list(result.get_points(measurement='light'))[0]['mean']
        except:
            pass
            
        if(light_avg < 200):
            GPIO.output(21, GPIO.HIGH) #turn LED on
        else:
            GPIO.output(21, GPIO.LOW) #turn LED off
            
    except KeyboardInterrupt:
        client.loop_stop() #stop client
        pass