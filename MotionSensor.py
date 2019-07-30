import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

_motion_in=31
_motion_out=12

#set in pin and out pin
GPIO.setup(_motion_in,GPIO.IN)
GPIO.setup(_motion_out,GPIO.OUT)

#check if there is a person
def check_people():
    return GPIO.input(_motion_in)==GPIO.HIGH

#turn on the motion sensored light
def light_motion_light():
    GPIO.output(_motion_out,True)

#turn off the motion sensored light
def dark_motion_light():
    GPIO.output(_motion_out,False)

dark_motion_light()

if __name__=='__main__':
    while True:
        if(GPIO.input(_motion_in)==GPIO.HIGH):
            light_motion_light()
        else:
            dark_motion_light()
        time.sleep(1)