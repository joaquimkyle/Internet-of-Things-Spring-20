#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi & MQTT parameters
#define WLAN_SSID "McSpanky's 2G"
#define WLAN_PASS "Lilypad420"
#define BROKER_IP "172.16.0.10"

// pin definitions
#define BUTTON 4
#define LED 5

// vars
bool buttonstate;
bool beenPressed = false;
bool ledOn = false;

WiFiClient client;
PubSubClient mqttclient(client);

void callback (char* topic, byte* payload, unsigned int length) {
  Serial.println(topic);
  Serial.write(payload, length);

  payload[length] = '\0'; //add null terminator to payload to read it as string
  
  if (strcmp(topic, "/arduino_led") == 0){
    if (strcmp((char *)payload, "on") == 0){
      digitalWrite(LED, HIGH);
    } else if (strcmp((char *)payload, "off") == 0){
      digitalWrite(LED, LOW);
    }
  }
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

  // setup pins
  pinMode(BUTTON, INPUT); // button setup as input
  pinMode(LED, OUTPUT); // LED pin setup as output
}

void loop() {
  if (!mqttclient.connected()) {
    connect();
  }

  // get button state
  buttonstate = digitalRead(BUTTON);

  // if button just pressed down
  if (buttonstate && !beenPressed) {
    beenPressed = true; //set pressed flag

    // toggle LED
    if (ledOn){
      mqttclient.publish("/pi_led", "off", false); // turn PI LED off
      ledOn = false;
    } else {
      mqttclient.publish("/pi_led", "on", false); // turn PI LED on
      ledOn = true;
    }
  }

  // if button is just released
  if (!buttonstate && beenPressed){
    beenPressed = false; //set pressed flag
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
