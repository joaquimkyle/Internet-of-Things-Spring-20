import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO
import datetime
from twilio.rest import Client

account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

#setup influxdb client
dbclient = InfluxDBClient('127.0.0.1', 8086, 'root', 'floho5310', 'plant')

#setup mqtt client
broker_address="172.16.0.10"

def on_message(client, userdata, message):
    print(message.topic + " " + message.payload.decode('UTF-8'))
    
    if(str(message.topic) == "/temperature"):
        receiveTime = datetime.datetime.utcnow()
        value = message.payload.decode('UTF-8')
        json_body = [
            {
                "measurement": 'temperature',
                "time": receiveTime,
                "fields": {
                    "value": float(value)
                }
            }
        ]
        
        dbclient.write_points(json_body)
        print("Finished writing to InfluxDB")
        temperature_handler(float(value))
        
    
    if(str(message.topic) == "/humidity"):
        receiveTime = datetime.datetime.utcnow()
        value = message.payload.decode('UTF-8')
        json_body = [
            {
                "measurement": 'humidity',
                "time": receiveTime,
                "fields": {
                    "value": float(value)
                }
            }
        ]
        
        dbclient.write_points(json_body)
        print("Finished writing to InfluxDB")
        humidity_handler(float(value))
        
    if(str(message.topic) == "/moisture"):
        receiveTime = datetime.datetime.utcnow()
        value = message.payload.decode('UTF-8')
        json_body = [
            {
                "measurement": 'moisture',
                "time": receiveTime,
                "fields": {
                    "value": float(value)
                }
            }
        ]
        
        dbclient.write_points(json_body)
        print("Finished writing to InfluxDB")
        moisture_handler(float(value))
        
        
def temperature_handler(value):
    if(value < 65):
        #turn on space heater
    elif(value > 75):
        #turn off space heater

def humidity_handler(value):
    if(value < 45):
        #turn on humidifer
    if(value > 55):
        #turn off humidifer

def moisture_handler(value):
    if(value < 20):
        #send dryness alert and turn off watering
        send_sms('Soil excessively dry, turning off pump system.')
        client.publish("/pump", "off")
    elif(value > 50):
        #send saturation alert and turn off watering
        send_sms('Soil oversaturated, turning off pump system.')
        client.publish("/pump", "off")
        
def send_sms(text)
    message = client.messages \
        .create(
            body=text,
            from_='+19145296888',
            to='+13393682390'
        )
     
    exec(open("send_sms.py").read())
    
        
        
client = mqtt.Client() #create new mqtt client instance
client.connect(broker_address) #connect to broker
client.subscribe("/temperature")
client.subscribe("/humidity")
client.subscribe("/moisture")
client.loop_start() #start client
client.on_message=on_message 

#loop
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
    
client.loop_stop() #stop mqtt client
GPIO.cleanup()
        