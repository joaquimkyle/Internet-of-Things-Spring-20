#define BUTTON 4
#define LED 5
bool buttonstate;
bool beenPressed = false;
bool ledOn = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(BUTTON, INPUT); // button setup as input
  pinMode(LED, OUTPUT); // LED pin setup as output
}

void loop() {
  // put your main code here, to run repeatedly:

  // get button state
  buttonstate = digitalRead(BUTTON);

  // if button just pressed down
  if (buttonstate && !beenPressed){

    // set pressed flag
    beenPressed = true;

    // toggle LED
    if (ledOn){
      digitalWrite(LED, LOW);
      ledOn = false;
    } 
    else{
      digitalWrite(LED, HIGH);
      ledOn = true;
    }
  }

  // if button just released
  if (!buttonstate && beenPressed){

    // set pressed flag
    beenPressed = false;
  }
}
