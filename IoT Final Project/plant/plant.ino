#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <stdio.h>
#include <stdlib.h>
#include <DHTesp.h>

//pin definitions
#define TEMPHUM 4
#define MOISTURE A0
#define PUMP 5

//Object setup
WiFiClient client;
PubSubClient mqttclient(client);
DHTesp dht;

//WiFi & MQTT parameters
#define WLAN_SSID "McSpanky's 2G"
#define WLAN_PASS "Lilypad420"
#define BROKER_IP "172.16.0.27"

//vars
int valueSize;
char* valueString;
float temperature;
float humidity;
float soilMoisture;
bool wateringFlag;

float readSoilMoisture(int analogPin) {
  // Read value and convert to voltage  
  int reading = analogRead(analogPin);
  float sensorVoltage = reading*(3.0 / 1023.0);
  float VWC;
  
  // Calculate Volumetric Water Conent
  if(sensorVoltage <= 1.1) {
    VWC = 10*sensorVoltage-1;
  } else if(sensorVoltage > 1.1 && sensorVoltage <= 1.3) {
    VWC = 25*sensorVoltage-17.5;
  } else if(sensorVoltage > 1.3 && sensorVoltage <= 1.82) {
    VWC = 48.08*sensorVoltage-47.5;
  } else if(sensorVoltage > 1.82) {
    VWC = 26.32*sensorVoltage-7.89;
  }
  return(VWC);
}

void callback (char* topic, byte* payload, unsigned int length) {
	Serial.println(topic);
	Serial.write(payload, length);
	
	payload[length] = '\0'; //add null terminator to payload to use as c-string 
	Serial.println("Checking topic...");
	if (strcmp(topic, "/pump") == 0) {
		if (strcmp((char *)payload, "on") == 0){
      wateringFlag = True;
    } else if (strcmp((char *)payload, "off") == 0){
      wateringFlag = False;
    }
	}
}

void setup() {
	Serial.begin(115200);
	
	//connect to WiFi
	WiFi.mode(WIFI_STA);
	WiFi.begin(WLAN_SSID, WLAN_PASS);
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.print(F("."));
	}

	Serial.println(F("WiFi connected"));
	Serial.println(F("IP address: "));
	Serial.println(WiFi.localIP());

	// connect to mqtt server
	mqttclient.setServer(BROKER_IP, 1883);
	mqttclient.setCallback(callback);
	connect();

    //configure pins
	pinMode(PUMP, OUTPUT); 
	pinMode(TEMPHUM, INPUT); 
	pinMode(MOISTURE, INPUT);
  digitalWrite(PUMP, LOW);
  wateringFlag = True;
  dht.setup(TEMPHUM, DHTesp::DHT11);
}

void loop() {
	if (!mqttclient.connected()) {
		connect();
	}

	//timekeeping variables
	static const unsigned long REFRESH_INTERVAL = 60000; // ms
	static unsigned long lastRefreshTime = 0;

	//if time between now and last update is more than time interval
	if(millis() - lastRefreshTime >= REFRESH_INTERVAL)
	{
		lastRefreshTime += REFRESH_INTERVAL;
		
        //read sensor values to variables
        TempAndHumidity values = dht.getTempAndHumidity();
        temperature = (values.temperature * 2) + 30; //fahrenheit conversion
        humidity = values.humidity;
        soilMoisture = readSoilMoisture(MOISTURE);
		
        //print sensor values to serial
        Serial.print("Temperature = ");
        Serial.println(temperature);
        Serial.print("Humidity = ");
        Serial.println(humidity);
        Serial.print("Soil VWC = ");
        Serial.println(soilMoisture);
        
        //send temperature
		    valueSize = snprintf(NULL, 0, "%f", temperature);
		    valueString = (char*)malloc(valueSize + 1);
		    snprintf(valueString, valueSize + 1, "%f", temperature);
		    mqttclient.publish("/temperature", valueString, false); //send reading to pi
        free(valueString);
        
        //send humidity
        valueSize = snprintf(NULL, 0, "%f", humidity);
		    valueString = (char*)malloc(valueSize + 1);
		    snprintf(valueString, valueSize + 1, "%f", humidity);
		    mqttclient.publish("/humidity", valueString, false); //send reading to pi
        free(valueString);
        
        //send moisture
        valueSize = snprintf(NULL, 0, "%f", soilMoisture);
        valueString = (char*)malloc(valueSize + 1);
        snprintf(valueString, valueSize + 1, "%f", soilMoisture);
        mqttclient.publish("/moisture", valueString, false); //send reading to pi
        free(valueString);

        //if soil VWC < 30, water about 1 oz by pumping 3 seconds
        if (soilMoisture < 30 && wateringFlag) {
          digitalWrite(PUMP, HIGH);
          delay(3000);
          digitalWrite(PUMP, LOW);
        }
	}

	mqttclient.loop();
}
	
void connect() {
	while (WiFi.status() != WL_CONNECTED) {
		Serial.println(F("WiFi issue"));
		delay(3000);
	}
	Serial.print(F("Connecting to MQTT server..."));
	while(!mqttclient.connected()) {
		if (mqttclient.connect(WiFi.macAddress().c_str())) {
			Serial.println(F("MQTT server Connected!"));

			//MQTT SUBSCRIPTIONS GO HERE
      mqttclient.subscribe("/pump");
		} else {
			Serial.print(F("MQTT server connected failed! rc="));
			Serial.print(mqttclient.state());
			Serial.println("try again in 10 seconds");
			// Wait 5 seconds before retrying
			delay(20000);
		}
	}
}
