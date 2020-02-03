#Kyle Joaquim

import RPi.GPIO as GPIO
import time

#setup board
GPIO.setmode(GPIO.BCM)

#setup pins
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.OUT)

#flag
beenPressed = False

#loop endlessly
while True:

    buttonstate = GPIO.input(21)
    
    if (buttonstate and not beenPressed):
        beenPressed = True
        GPIO.output(23, GPIO.HIGH)
        
    if (not buttonstate and beenPressed):
        beenPressed = False
        GPIO.output(23, GPIO.LOW)