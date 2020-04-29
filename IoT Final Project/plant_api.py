import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from flask import Flask, request, json
from flask_restful import Resource, Api
from twilio.twiml.messaging_response import MessagingResponse
import datetime

broker_address="172.16.0.10"

client = mqtt.Client()
client.connect(broker_address)
client.loop_start()

dbclient = InfluxDBClient('127.0.0.1', 8086, 'root', 'floho5310', 'plant')

app = Flask(__name__)
api = Api(app)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    #Get the message sent to Twilio number
    body = request.values.get('Body', None)
    
    if body == 'data':
        query1 = 'select mean("value") from "temperature" where "time" > now() - 604800s'
        query2 = 'select mean("value") from "humidity" where "time" > now() - 604800s'
        result1 = dbclient.query(query1)
        result2 = dbclient.query(query2)
        try:
            temp_avg = list(result1.get_points(measurement='temperature'))[0]['mean']
        except:
            pass
            
        try:
            hum_avg = list(result2.get_points(measurement='humidity'))[0]['mean']
        except:
            pass
            
        resp = MessagingResponse()
        msg = resp.message("Average temperature over 7 days: " + temp_avg + "\nAverage humidity over 7 days: " + hum_avg)
        
        return str(resp)
        
    
    elif body == 'pump on':
        client.publish("/pump", "on")
    
    elif body == 'pump off':
        client.publish("/pump", "off")

app.run(host='127.0.0.1', debug=True)

try:
    while True:
        pass
except KeyboardInterrupt:
    pass
    
client.loop_stop() #stop mqtt client