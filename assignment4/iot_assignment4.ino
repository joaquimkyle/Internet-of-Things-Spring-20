#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <stdio.h>
#include <stdlib.h>

// WiFi & MQTT parameters
#define WLAN_SSID "McSpanky's 2G"
#define WLAN_PASS "Lilypad420"
#define BROKER_IP "172.16.0.10"

// vars
int lightstate;
char* valueString;
int valueSize;

WiFiClient client;
PubSubClient mqttclient(client);

void callback (char* topic, byte* payload, unsigned int length) {
  //do nothing
}

void setup() {
  Serial.begin(115200);

  // connect to WiFi
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
}

void loop() {
  if (!mqttclient.connected()) {
    connect();
  }

  //timekeeping variables
  static const unsigned long REFRESH_INTERVAL = 1000; // ms
  static unsigned long lastRefreshTime = 0;

  //if time between now and last update is more than time interval
  if(millis() - lastRefreshTime >= REFRESH_INTERVAL)
  {
    lastRefreshTime += REFRESH_INTERVAL;
    lightstate = analogRead(A0);
    Serial.println(lightstate);

    valueSize = snprintf(NULL, 0, "%d", lightstate);
    valueString = (char*)malloc(valueSize + 1);
    snprintf(valueString, valueSize + 1, "%d", lightstate);
    
    mqttclient.publish("/pi_led", valueString, false); //send analog reading to pi

    free(valueString);
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

      mqttclient.subscribe("/arduino_led");
    } else {
      Serial.print(F("MQTT server connected failed! rc="));
      Serial.print(mqttclient.state());
      Serial.println("try again in 10 seconds");
      // Wait 5 seconds before retrying
      delay(20000);
    }
  }
}
