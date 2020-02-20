import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from flask import Flask, request, json
from flask_restful import Resource, Api
import datetime

broker_address="172.16.0.10"

client = mqtt.Client()
client.connect(broker_address)
client.loop_start()

dbclient = InfluxDBClient('127.0.0.1', 8086, 'root', 'floho5310', 'mydb')

app = Flask(__name__)
api = Api(app)

class Lights(Resource):
    def get(self):
        query = 'select mean("value") from "light" where "time" > now() - 10s'
        result = dbclient.query(query)
        try:
            light_avg = list(result.get_points(measurement='light'))[0]['mean']
        except:
            pass
            
        return {'average':light_avg}
        
    def post(self):
        value = request.get_data()
        value = json.loads(value)
        if(value['device'] == 'pi'):
            if(value['state'] == 'on'):
                client.publish("/pi_led", "on")
            elif(value['state'] == 'off'):
                client.publish("/pi_led", "off")
        elif(value['device'] == 'arduino'):
            if(value['state'] == 'on'):
                client.publish("/arduino_led", "on")
            elif(value['state'] == 'off'):
                client.publish("/arduino_led", "off")

               
api.add_resource(Lights, '/lights')

app.run(host='127.0.0.1', debug=True)

try:
    while True:
        pass
except KeyboardInterrupt:
    pass
    
client.loop_stop() #stop mqtt client