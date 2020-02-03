#Kyle Joaquim

import RPi.GPIO as GPIO
import time

#setup board
GPIO.setmode(GPIO.BCM)

#setup pins
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.OUT)

#flags
beenPressed = False
ledOn = False

#loop endlessly
while True:

    #get button state
    buttonstate = GPIO.input(21)
    
    #if button just pressed down
    if (buttonstate and not beenPressed):
        
        #set pressed flag
        beenPressed = True
        
        #toggle LED
        if (ledOn):
            GPIO.output(23, GPIO.LOW)
            ledOn = False
        else:
            GPIO.output(23, GPIO.HIGH)
            ledOn = True
        
    #if button just released    
    if (not buttonstate and beenPressed):
        
        #set pressed flag
        beenPressed = False